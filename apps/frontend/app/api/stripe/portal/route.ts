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
  return new Stripe(key, { apiVersion: '2024-12-18.acacia' as any });
}

export async function POST(req: NextRequest) {
  try {
    const { userId } = await auth();
    const origin = req.headers.get('origin') || process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  const stripe = await getStripe();

    // In Phase 4 we don’t persist Stripe customers. We let Stripe create guests during checkout.
    // To access portal, a customer must exist. For now, we create a new customer for the user if signed in.
    let customerId: string | undefined;
    if (userId) {
      const customer = await stripe.customers.create({ metadata: { clerk_user_id: userId } });
      customerId = customer.id;
    }

    if (!customerId) {
      return NextResponse.json({ error: 'No customer available for portal.' }, { status: 400 });
    }

    const session = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: `${origin}/billing`,
    });

    return NextResponse.json({ url: session.url }, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || 'stripe_error' }, { status: 500 });
  }
}
