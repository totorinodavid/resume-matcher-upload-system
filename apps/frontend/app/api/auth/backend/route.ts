import { NextRequest, NextResponse } from 'next/server';
import { auth } from "@/auth";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

interface BackendUser {
  id: string;
  email: string;
  name?: string;
  picture?: string;
  provider: 'google';
  created_at: string;
}

/**
 * Backend Authentication API
 * Creates and validates backend-compatible tokens for users
 */

export async function POST(req: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json(
        { error: 'AUTHENTICATION_REQUIRED', detail: 'No valid session found' },
        { status: 401 }
      );
    }

    // Create backend user record
    const backendUser: BackendUser = {
      id: session.user.id,
      email: session.user.email!,
      name: session.user.name || undefined,
      picture: session.user.image || undefined,
      provider: 'google',
      created_at: new Date().toISOString()
    };

    // Create a backend-compatible JWT token
    const tokenPayload = {
      sub: backendUser.id,
      email: backendUser.email,
      name: backendUser.name,
      picture: backendUser.picture,
      provider: backendUser.provider,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
      iss: 'gojob.ing',
      aud: 'resume-matcher-api'
    };

    // In production, you'd sign this with a secret key that the backend knows
    // For now, we'll create a structured token that the backend can parse
    const token = `gojob_${Buffer.from(JSON.stringify(tokenPayload)).toString('base64url')}`;

    // Log successful authentication for debugging
    console.log('Backend authentication successful:', {
      userId: backendUser.id,
      email: backendUser.email,
      tokenIssued: new Date().toISOString()
    });

    return NextResponse.json({
      success: true,
      user: backendUser,
      token: token,
      expires_at: new Date(Date.now() + (24 * 60 * 60 * 1000)).toISOString()
    });

  } catch (error) {
    console.error('Backend authentication error:', error);
    return NextResponse.json(
      { error: 'AUTHENTICATION_FAILED', detail: 'Failed to create backend authentication' },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const session = await auth();
    
    if (!session?.user) {
      return NextResponse.json(
        { error: 'AUTHENTICATION_REQUIRED', detail: 'No valid session found' },
        { status: 401 }
      );
    }

    // Return current user info for backend validation
    return NextResponse.json({
      authenticated: true,
      user: {
        id: session.user.id,
        email: session.user.email,
        name: session.user.name,
        picture: session.user.image,
        provider: 'google'
      },
      session_valid: true
    });

  } catch (error) {
    console.error('Session validation error:', error);
    return NextResponse.json(
      { error: 'SESSION_VALIDATION_FAILED', detail: 'Failed to validate session' },
      { status: 500 }
    );
  }
}
