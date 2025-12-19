import { NextRequest, NextResponse } from 'next/server';

// Use server-side environment variable (not exposed to client bundle)
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Request timeout in milliseconds
const REQUEST_TIMEOUT_MS = 10000;

// Structured logger for audit trails
function auditLog(event: string, data: Record<string, unknown>) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    service: 'frontend-auth',
    event,
    ...data,
  };
  console.log(JSON.stringify(logEntry));
}

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const clientIp = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
  const refreshToken = request.cookies.get('refresh_token')?.value;

  if (!refreshToken) {
    auditLog('token_refresh_attempt', {
      requestId,
      clientIp,
      status: 'failed',
      reason: 'no_refresh_token',
    });
    return NextResponse.json(
      { detail: 'No refresh token' },
      { status: 401 }
    );
  }

  auditLog('token_refresh_attempt', {
    requestId,
    clientIp,
    status: 'initiated',
  });

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let res: Response;
  try {
    res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
      signal: controller.signal,
    });
  } catch (fetchError) {
    clearTimeout(timeoutId);

    const isTimeout = fetchError instanceof Error && fetchError.name === 'AbortError';
    const reason = isTimeout ? 'timeout' : 'network_error';

    auditLog('token_refresh_attempt', {
      requestId,
      clientIp,
      status: 'failed',
      reason,
    });

    return NextResponse.json(
      { detail: isTimeout ? 'Request timed out. Please try again.' : 'Unable to connect to the server' },
      { status: 503 }
    );
  } finally {
    clearTimeout(timeoutId);
  }

  // Handle non-JSON responses gracefully
  let data: Record<string, unknown>;
  try {
    data = await res.json();
  } catch {
    auditLog('token_refresh_attempt', {
      requestId,
      clientIp,
      status: 'failed',
      reason: 'invalid_backend_response',
      backendStatus: res.status,
    });
    return NextResponse.json(
      { detail: 'Unexpected response from server' },
      { status: 502 }
    );
  }

  if (!res.ok) {
    auditLog('token_refresh_attempt', {
      requestId,
      clientIp,
      status: 'failed',
      reason: 'backend_rejected',
      backendStatus: res.status,
    });

    // Clear cookies if refresh failed
    const response = NextResponse.json(
      { detail: typeof data.detail === 'string' ? data.detail : 'Token refresh failed' },
      { status: res.status }
    );
    response.cookies.delete('token');
    response.cookies.delete('refresh_token');
    return response;
  }

  auditLog('token_refresh_attempt', {
    requestId,
    clientIp,
    status: 'success',
  });

  // Update access token cookie
  const response = NextResponse.json({ success: true });
  const isProduction = process.env.NODE_ENV === 'production';

  if (typeof data.access_token === 'string') {
    response.cookies.set('token', data.access_token, {
      httpOnly: true,
      secure: isProduction,
      sameSite: 'lax',
      maxAge: 30 * 60, // 30 minutes
      path: '/',
    });
  }

  return response;
}
