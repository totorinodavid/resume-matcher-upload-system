import { auth, currentUser } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const { userId, getToken, sessionId } = auth();
    const user = await currentUser().catch(() => null);
    let jwt: string | null = null;
    let tokenError: string | null = null;

    try {
      jwt = await getToken({ template: process.env.CLERK_JWT_TEMPLATE || undefined });
    } catch (e: any) {
      tokenError = e?.message || 'token_mint_failed';
    }

    return NextResponse.json({
      ok: true,
      sessionId: sessionId || null,
      userId: userId || null,
      email: user?.primaryEmailAddress?.emailAddress || null,
      hasToken: Boolean(jwt),
      tokenPreview: jwt ? jwt.slice(0, 24) + '...' : null,
      tokenError,
      template: process.env.CLERK_JWT_TEMPLATE || null,
    });
  } catch (err: any) {
    return NextResponse.json({ ok: false, error: err?.message || 'unknown' }, { status: 500 });
  }
}
