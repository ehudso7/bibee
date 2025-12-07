import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const token = request.cookies.get('token')?.value;

    // Call backend logout to invalidate token
    if (token) {
      try {
        await fetch(`${API_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      } catch {
        // Ignore backend errors during logout
      }
    }

    // Clear cookies regardless of backend response
    const response = NextResponse.json({ success: true });
    response.cookies.delete('token');
    response.cookies.delete('refresh_token');

    return response;
  } catch (error) {
    console.error('Logout error:', error);
    // Still clear cookies on error
    const response = NextResponse.json({ success: true });
    response.cookies.delete('token');
    response.cookies.delete('refresh_token');
    return response;
  }
}
