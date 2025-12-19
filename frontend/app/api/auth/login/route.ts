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

// Input validation
interface LoginInput {
  email?: unknown;
  password?: unknown;
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  sanitized?: {
    email: string;
    password: string;
  };
}

function validateLoginInput(input: LoginInput): ValidationResult {
  const errors: string[] = [];

  // Validate email
  if (!input.email || typeof input.email !== 'string') {
    errors.push('Email is required');
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(input.email)) {
      errors.push('Invalid email format');
    }
  }

  // Validate password
  if (!input.password || typeof input.password !== 'string') {
    errors.push('Password is required');
  }

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  return {
    valid: true,
    errors: [],
    sanitized: {
      email: (input.email as string).toLowerCase().trim(),
      password: input.password as string,
    },
  };
}

export async function POST(request: NextRequest) {
  const requestId = crypto.randomUUID();
  const clientIp = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';

  try {
    // Parse request body
    let body: LoginInput;
    try {
      body = await request.json();
    } catch {
      auditLog('login_attempt', {
        requestId,
        clientIp,
        status: 'failed',
        reason: 'invalid_json',
      });
      return NextResponse.json(
        { detail: 'Invalid JSON in request body' },
        { status: 400 }
      );
    }

    // Validate input
    const validation = validateLoginInput(body);
    if (!validation.valid) {
      auditLog('login_attempt', {
        requestId,
        clientIp,
        email: typeof body.email === 'string' ? body.email : undefined,
        status: 'failed',
        reason: 'validation_failed',
      });
      return NextResponse.json(
        { detail: validation.errors.join('; ') },
        { status: 400 }
      );
    }

    const { sanitized } = validation;

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    auditLog('login_attempt', {
      requestId,
      clientIp,
      email: sanitized!.email,
      status: 'initiated',
    });

    let res: Response;
    try {
      res = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitized),
        signal: controller.signal,
      });
    } catch (fetchError) {
      clearTimeout(timeoutId);

      const isTimeout = fetchError instanceof Error && fetchError.name === 'AbortError';
      const reason = isTimeout ? 'timeout' : 'network_error';

      auditLog('login_attempt', {
        requestId,
        clientIp,
        email: sanitized!.email,
        status: 'failed',
        reason,
      });

      return NextResponse.json(
        { detail: isTimeout ? 'Request timed out. Please try again.' : 'Unable to connect to the server. Please try again later.' },
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
      auditLog('login_attempt', {
        requestId,
        clientIp,
        email: sanitized!.email,
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
      // Use generic message for auth failures to prevent user enumeration
      const safeDetail = res.status === 401
        ? 'Invalid email or password'
        : (typeof data.detail === 'string' ? data.detail : 'Login failed');

      auditLog('login_attempt', {
        requestId,
        clientIp,
        email: sanitized!.email,
        status: 'failed',
        reason: 'invalid_credentials',
        backendStatus: res.status,
      });

      return NextResponse.json(
        { detail: safeDetail },
        { status: res.status }
      );
    }

    auditLog('login_attempt', {
      requestId,
      clientIp,
      email: sanitized!.email,
      status: 'success',
    });

    // Create response with secure cookies
    const response = NextResponse.json({
      success: true,
      user: data.user,
    });

    const isProduction = process.env.NODE_ENV === 'production';

    // Set access token cookie (HttpOnly for security - accessed via /api/proxy)
    if (typeof data.access_token === 'string') {
      response.cookies.set('token', data.access_token, {
        httpOnly: true,
        secure: isProduction,
        sameSite: 'lax',
        maxAge: 30 * 60, // 30 minutes (matches backend)
        path: '/',
      });
    }

    // Set refresh token cookie (HttpOnly, secure)
    if (typeof data.refresh_token === 'string') {
      response.cookies.set('refresh_token', data.refresh_token, {
        httpOnly: true,
        secure: isProduction,
        sameSite: 'strict',
        maxAge: 7 * 24 * 60 * 60, // 7 days (matches backend)
        path: '/',
      });
    }

    return response;
  } catch (error) {
    // Log error without sensitive details
    auditLog('login_error', {
      requestId,
      clientIp,
      status: 'error',
      errorType: error instanceof Error ? error.name : 'UnknownError',
    });

    return NextResponse.json(
      { detail: 'An unexpected error occurred during login' },
      { status: 500 }
    );
  }
}
