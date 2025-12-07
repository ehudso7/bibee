import { NextRequest, NextResponse } from 'next/server';

// Use server-side environment variable (not exposed to client bundle)
const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Request timeout in milliseconds
const REQUEST_TIMEOUT_MS = 5000;

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
  const token = request.cookies.get('token')?.value;

  auditLog('logout_attempt', {
    requestId,
    clientIp,
    hasToken: !!token,
    status: 'initiated',
  });

  // Call backend logout to invalidate token
  if (token) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      await fetch(`${API_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      auditLog('logout_attempt', {
        requestId,
        clientIp,
        status: 'success',
        backendNotified: true,
      });
    } catch (fetchError) {
      const isTimeout = fetchError instanceof Error && fetchError.name === 'AbortError';

      // Log but don't fail - we still want to clear cookies
      auditLog('logout_attempt', {
        requestId,
        clientIp,
        status: 'partial',
        backendNotified: false,
        reason: isTimeout ? 'timeout' : 'network_error',
      });
    } finally {
      clearTimeout(timeoutId);
    }
  } else {
    auditLog('logout_attempt', {
      requestId,
      clientIp,
      status: 'success',
      backendNotified: false,
      reason: 'no_token',
    });
  }

  // Clear cookies regardless of backend response
  const response = NextResponse.json({ success: true });
  response.cookies.delete('token');
  response.cookies.delete('refresh_token');

  return response;
}
