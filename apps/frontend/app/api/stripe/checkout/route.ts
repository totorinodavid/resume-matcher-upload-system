import { NextRequest, NextResponse } from 'next/server';
import { auth } from "@/auth";
import { CreditProducts } from '@/lib/stripe/products';

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
  // Use a valid Stripe API version (date-only). Remove or update as needed per your account settings.
  return new Stripe(key, { apiVersion: '2023-10-16' });
}

export async function POST(req: NextRequest) {
  try {
    const authSession = await auth();
    let userId = authSession?.user?.id;
    // E2E bypass: allow tests to simulate a signed-in user via header when enabled
    if (!userId && (process.env.E2E_TEST_MODE === '1' || process.env.E2E_TEST_MODE === 'true')) {
      const e2eUser = req.headers.get('x-e2e-user') || req.cookies.get('x-e2e-user')?.value;
      if (e2eUser) userId = e2eUser;
    }
    // Require sign-in for purchasing credits to ensure webhook can map the user reliably
    if (!userId) {
      return NextResponse.json({ error: 'Sign-in required to purchase credits' }, { status: 401 });
    }
    const body = await req.json().catch(() => ({}));
    const price_id = String(body?.price_id || '').trim();
    if (!price_id) return NextResponse.json({ error: 'price_id required' }, { status: 400 });

  const stripe = await getStripe();

  // Success/Cancel URLs – ensure NEXT_PUBLIC_SITE_URL is set in production
    const origin = req.headers.get('origin') || process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
    const success_url = `${origin}/billing?status=success`;
    const cancel_url = `${origin}/billing?status=cancel`;

    // Determine credits for the selected price to store in metadata for webhook fulfillment
    // Disallow placeholder prices — enforce real configured IDs
    const plan = CreditProducts.find((p) => p.price_id === price_id && !p.price_id.endsWith('_placeholder'));
    if (!plan) {
      return NextResponse.json({ error: 'Unknown or placeholder price_id. Configure NEXT_PUBLIC_STRIPE_PRICE_* envs.' }, { status: 400 });
    }
    const credits = plan.credits;
    const plan_id = plan.id;

  const stripeSession = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: price_id, quantity: 1 }],
  // Helps us correlate session to NextAuth user in dashboards/logs
  client_reference_id: userId || undefined,
      // Optionally collect customer information; when you add real customer mapping, pass customer if known.
      // Store NextAuth user id and credit info so the webhook can fulfill immediately without extra lookups.
      // Stripe requires metadata values to be strings.
      metadata: {
        ...(userId ? { user_id: String(userId) } : {}),
        price_id: String(price_id),
        ...(plan_id ? { plan_id: String(plan_id) } : {}),
        credits: String(credits),
      },
      success_url,
      cancel_url,
      // For credits, we’ll use metadata in Phase 5 to record the credit amount server-side
    });

    return NextResponse.json({ url: stripeSession.url }, { status: 200 });
  } catch (err: unknown) {
    const error = err as Error & { message?: string };
    return NextResponse.json({ error: error?.message || 'stripe_error' }, { status: 500 });
  }
}
