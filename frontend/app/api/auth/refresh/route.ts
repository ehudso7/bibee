import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const refreshToken = request.cookies.get('refresh_token')?.value;

    if (!refreshToken) {
      return NextResponse.json(
        { detail: 'No refresh token' },
        { status: 401 }
      );
    }

    // Forward refresh request to backend
    const res = await fetch(`${API_URL}/api/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const data = await res.json();

    if (!res.ok) {
      // Clear cookies if refresh failed
      const response = NextResponse.json(
        { detail: data.detail || 'Token refresh failed' },
        { status: res.status }
      );
      response.cookies.delete('token');
      response.cookies.delete('refresh_token');
      return response;
    }

    // Update access token cookie
    const response = NextResponse.json({ success: true });
    const isProduction = process.env.NODE_ENV === 'production';

    response.cookies.set('token', data.access_token, {
      httpOnly: false, // Needed for client-side API calls
      secure: isProduction,
      sameSite: 'lax',
      maxAge: 30 * 60, // 30 minutes
      path: '/',
    });

    return response;
  } catch (error) {
    console.error('Token refresh error:', error);
    return NextResponse.json(
      { detail: 'An error occurred during token refresh' },
      { status: 500 }
    );
  }
}
