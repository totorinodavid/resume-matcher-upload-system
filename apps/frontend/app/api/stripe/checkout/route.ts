import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

// Node runtime required for Stripe SDK
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';
export const maxDuration = 30;

async function getStripe() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error('Missing STRIPE_SECRET_KEY');
  const Stripe = (await import('stripe')).default;
  return new Stripe(key, { apiVersion: '2024-12-18.acacia' as any });
}

export async function POST(req: NextRequest) {
  try {
    const { userId } = await auth();
    // Clerk is optional here; we can still create a session without a user, but prefer linking
    const body = await req.json().catch(() => ({}));
    const price_id = String(body?.price_id || '').trim();
    if (!price_id) return NextResponse.json({ error: 'price_id required' }, { status: 400 });

  const stripe = await getStripe();

  // Success/Cancel URLs – ensure NEXT_PUBLIC_SITE_URL is set in production
    const origin = req.headers.get('origin') || process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
    const success_url = `${origin}/billing?status=success`;
    const cancel_url = `${origin}/billing?status=cancel`;

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: price_id, quantity: 1 }],
      // Optionally collect customer information; when you add real customer mapping, pass customer if known.
      metadata: userId ? { clerk_user_id: userId } : undefined,
      success_url,
      cancel_url,
      // For credits, we’ll use metadata in Phase 5 to record the credit amount server-side
    });

    return NextResponse.json({ url: session.url }, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || 'stripe_error' }, { status: 500 });
  }
}
