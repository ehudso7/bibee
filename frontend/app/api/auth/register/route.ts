import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward registration request to backend
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { detail: data.detail || 'Registration failed' },
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
interface RegistrationInput {
  name?: unknown;
  email?: unknown;
  password?: unknown;
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  sanitized?: {
    name: string;
    email: string;
    password: string;
  };
}

function validateRegistrationInput(input: RegistrationInput): ValidationResult {
  const errors: string[] = [];

  // Validate name
  if (!input.name || typeof input.name !== 'string') {
    errors.push('Name is required and must be a string');
  } else if (input.name.trim().length < 1 || input.name.trim().length > 100) {
    errors.push('Name must be between 1 and 100 characters');
  }

  // Validate email
  if (!input.email || typeof input.email !== 'string') {
    errors.push('Email is required and must be a string');
  } else {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(input.email)) {
      errors.push('Invalid email format');
    }
    if (input.email.length > 254) {
      errors.push('Email must not exceed 254 characters');
    }
  }

  // Validate password
  if (!input.password || typeof input.password !== 'string') {
    errors.push('Password is required and must be a string');
  } else {
    if (input.password.length < 8) {
      errors.push('Password must be at least 8 characters');
    }
    if (input.password.length > 72) {
      errors.push('Password must not exceed 72 characters');
    }
    if (!/[A-Z]/.test(input.password)) {
      errors.push('Password must contain at least one uppercase letter');
    }
    if (!/[a-z]/.test(input.password)) {
      errors.push('Password must contain at least one lowercase letter');
    }
    if (!/\d/.test(input.password)) {
      errors.push('Password must contain at least one digit');
    }
  }

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  return {
    valid: true,
    errors: [],
    sanitized: {
      name: (input.name as string).trim(),
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
    let body: RegistrationInput;
    try {
      body = await request.json();
    } catch {
      auditLog('registration_attempt', {
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
    const validation = validateRegistrationInput(body);
    if (!validation.valid) {
      auditLog('registration_attempt', {
        requestId,
        clientIp,
        email: typeof body.email === 'string' ? body.email : undefined,
        status: 'failed',
        reason: 'validation_failed',
        errors: validation.errors,
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

    auditLog('registration_attempt', {
      requestId,
      clientIp,
      email: sanitized!.email,
      status: 'initiated',
    });

    let res: Response;
    try {
      res = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sanitized),
        signal: controller.signal,
      });
    } catch (fetchError) {
      clearTimeout(timeoutId);

      const isTimeout = fetchError instanceof Error && fetchError.name === 'AbortError';
      const reason = isTimeout ? 'timeout' : 'network_error';

      auditLog('registration_attempt', {
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
      auditLog('registration_attempt', {
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
      // Sanitize error message - don't expose internal details
      const safeDetail = typeof data.detail === 'string'
        ? data.detail
        : 'Registration failed';

      auditLog('registration_attempt', {
        requestId,
        clientIp,
        email: sanitized!.email,
        status: 'failed',
        reason: 'backend_rejected',
        backendStatus: res.status,
      });

      return NextResponse.json(
        { detail: safeDetail },
        { status: res.status }
      );
    }

    // Return user data on successful registration
    return NextResponse.json(data);
  } catch (error) {
    console.error('Registration error:', error);
    return NextResponse.json(
      { detail: 'An error occurred during registration' },
    auditLog('registration_attempt', {
      requestId,
      clientIp,
      email: sanitized!.email,
      status: 'success',
    });

    // Return user data on successful registration (excluding sensitive fields)
    return NextResponse.json({
      id: data.id,
      email: data.email,
      name: data.name,
    });
  } catch (error) {
    // Log error without sensitive details
    auditLog('registration_error', {
      requestId,
      clientIp,
      status: 'error',
      errorType: error instanceof Error ? error.name : 'UnknownError',
    });

    return NextResponse.json(
      { detail: 'An unexpected error occurred during registration' },
      { status: 500 }
    );
  }
}
