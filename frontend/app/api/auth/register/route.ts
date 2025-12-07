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
        { status: res.status }
      );
    }

    // Return user data on successful registration
    return NextResponse.json(data);
  } catch (error) {
    console.error('Registration error:', error);
    return NextResponse.json(
      { detail: 'An error occurred during registration' },
      { status: 500 }
    );
  }
}
