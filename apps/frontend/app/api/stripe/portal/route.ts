import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';
export const maxDuration = 30;

async function getStripe() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error('Missing STRIPE_SECRET_KEY');
  const Stripe = (await import('stripe')).default;
  return new Stripe(key);
}

export async function POST(req: NextRequest) {
  try {
    const { userId } = await auth();
    const origin = req.headers.get('origin') || process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  const stripe = await getStripe();

    // Customer Portal requires an existing Stripe customer. Do not create a blank
    // customer here, because it will not be linked to any payments.
    // Expect the customer to be created during Checkout.
    const custSearch = userId
      ? await stripe.customers.search({
          // Search by metadata set at checkout time
          query: `metadata['clerk_user_id']:'${userId}'`,
        })
      : null;
    const customerId = custSearch?.data?.[0]?.id;
    if (!customerId) return NextResponse.json({ error: 'Kein zugehöriger Stripe-Kunde gefunden.' }, { status: 400 });

    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: `${origin}/billing`,
    });

    return NextResponse.json({ url: session.url }, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || 'stripe_error' }, { status: 500 });
  }
}
