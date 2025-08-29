import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/auth';

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
  return new Stripe(key, { apiVersion: '2024-12-18' as any });
}

export async function POST(req: NextRequest) {
  try {
  const session = await auth();
  let userId = session?.user?.id as string | undefined;
    if (!userId && (process.env.E2E_TEST_MODE === '1' || process.env.E2E_TEST_MODE === 'true')) {
      const e2eUser = req.headers.get('x-e2e-user') || req.cookies.get('x-e2e-user')?.value;
      if (e2eUser) userId = e2eUser;
    }
    const origin = req.headers.get('origin') || process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  const stripe = await getStripe();

    // In Phase 4 we don’t persist Stripe customers. We let Stripe create guests during checkout.
    // To access portal, a customer must exist. For now, we create a new customer for the user if signed in.
    let customerId: string | undefined;
  if (userId) {
      const customer = await stripe.customers.create({ metadata: { user_id: userId } });
      customerId = customer.id;
    }

    if (!customerId) {
      return NextResponse.json({ error: 'No customer available for portal.' }, { status: 400 });
    }

  const portalSession = await stripe.billingPortal.sessions.create({
      customer: customerId,
      return_url: `${origin}/billing`,
    });

  return NextResponse.json({ url: portalSession.url }, { status: 200 });
  } catch (err: any) {
    return NextResponse.json({ error: err?.message || 'stripe_error' }, { status: 500 });
  }
}
