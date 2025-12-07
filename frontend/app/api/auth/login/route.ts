import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Forward login request to backend
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json();

    if (!res.ok) {
      return NextResponse.json(
        { detail: data.detail || 'Login failed' },
        { status: res.status }
      );
    }

    // Create response with secure cookies
    const response = NextResponse.json({
      success: true,
      user: data.user,
    });

    const isProduction = process.env.NODE_ENV === 'production';

    // Set access token cookie (short-lived, accessible by JS for API calls)
    response.cookies.set('token', data.access_token, {
      httpOnly: false, // Needed for client-side API calls with Bearer token
      secure: isProduction,
      sameSite: 'lax',
      maxAge: 30 * 60, // 30 minutes (matches backend)
      path: '/',
    });

    // Set refresh token cookie (HttpOnly, secure)
    response.cookies.set('refresh_token', data.refresh_token, {
      httpOnly: true,
      secure: isProduction,
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60, // 7 days (matches backend)
      path: '/',
    });

    return response;
  } catch (error) {
    console.error('Login error:', error);
    return NextResponse.json(
      { detail: 'An error occurred during login' },
      { status: 500 }
    );
  }
}
