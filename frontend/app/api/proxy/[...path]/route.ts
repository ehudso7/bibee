import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * API Proxy Route - Secure Backend-for-Frontend (BFF) Pattern
 *
 * This proxy handles all API requests to the backend, keeping tokens
 * in HttpOnly cookies. This prevents XSS attacks from stealing tokens
 * since JavaScript cannot access HttpOnly cookies.
 *
 * Usage: /api/proxy/users/me -> Backend: /api/users/me
 */

async function proxyRequest(request: NextRequest, path: string): Promise<NextResponse> {
  const token = request.cookies.get('token')?.value;
  const url = `${API_URL}/api/${path}`;

  // Build headers, forwarding auth token if present
  const headers: HeadersInit = {
    ...(token && { Authorization: `Bearer ${token}` }),
  };

  // For requests with body, forward content-type and body
  // Store body content for potential retry after token refresh
  let body: BodyInit | undefined;
  let bodyForRetry: BodyInit | undefined;
  const contentType = request.headers.get('content-type');

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    if (contentType?.includes('application/json')) {
      headers['Content-Type'] = 'application/json';
      const bodyText = await request.text();
      body = bodyText;
      bodyForRetry = bodyText;
    } else if (contentType?.includes('multipart/form-data')) {
      // For file uploads, clone the request to read body twice if needed
      const bodyBuffer = await request.arrayBuffer();
      body = bodyBuffer;
      bodyForRetry = bodyBuffer.slice(0); // Clone for retry
      headers['Content-Type'] = contentType;
    }
  }

  try {
    const res = await fetch(url, {
      method: request.method,
      headers,
      body,
    });

    // Handle token refresh on 401
    if (res.status === 401) {
      // Try to refresh the token
      const refreshToken = request.cookies.get('refresh_token')?.value;
      if (refreshToken) {
        // Send refresh token in body as expected by backend
        const refreshRes = await fetch(`${API_URL}/api/auth/refresh`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshToken }),
        });

        if (refreshRes.ok) {
          const refreshData = await refreshRes.json();

          // Retry the original request with new token
          const retryRes = await fetch(url, {
            method: request.method,
            headers: {
              ...headers,
              Authorization: `Bearer ${refreshData.access_token}`,
            },
            body: bodyForRetry,
          });

          const retryData = await retryRes.text();
          const response = new NextResponse(retryData, {
            status: retryRes.status,
            headers: { 'Content-Type': retryRes.headers.get('content-type') || 'application/json' },
          });

          // Update the access token cookie
          const isProduction = process.env.NODE_ENV === 'production';
          response.cookies.set('token', refreshData.access_token, {
            httpOnly: true,
            secure: isProduction,
            sameSite: 'lax',
            maxAge: 30 * 60,
            path: '/',
          });

          return response;
        }
      }
    }

    // Forward the response
    const data = await res.text();
    return new NextResponse(data, {
      status: res.status,
      headers: { 'Content-Type': res.headers.get('content-type') || 'application/json' },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to connect to backend service' },
      { status: 503 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/') + (request.nextUrl.search || '');
  return proxyRequest(request, pathStr);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/') + (request.nextUrl.search || '');
  return proxyRequest(request, pathStr);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/') + (request.nextUrl.search || '');
  return proxyRequest(request, pathStr);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/') + (request.nextUrl.search || '');
  return proxyRequest(request, pathStr);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join('/') + (request.nextUrl.search || '');
  return proxyRequest(request, pathStr);
}
