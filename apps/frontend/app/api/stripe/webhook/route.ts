import type { NextRequest } from 'next/server';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;

// We will forward the verified event to the backend credits webhook which owns DB writes,
// to keep a single source of truth and avoid duplicating SQL clients here.
// This route only verifies signature and ensures idempotency is handled downstream by backend's unique index.

export async function POST(req: NextRequest) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  const key = process.env.STRIPE_SECRET_KEY;
  if (!secret || !key) {
    return new Response('Stripe not configured', { status: 503 });
  }

  const rawBody = await req.text();
  const sig = req.headers.get('stripe-signature') || req.headers.get('Stripe-Signature');
  if (!sig) return new Response('Missing signature', { status: 400 });

  try {
    const Stripe = (await import('stripe')).default;
    const stripe = new Stripe(key, { apiVersion: '2024-12-18.acacia' as any });
    // Throws if invalid
    const event = stripe.webhooks.constructEvent(rawBody, sig, secret);
    // For now, forward to backend which persists credits idempotently.
    const backend = (process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || 'https://resume-matcher-backend-j06k.onrender.com').replace(/\/$/, '');
    // Preserve the original headers and body
    const res = await fetch(`${backend}/webhooks/stripe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Stripe-Signature': sig,
      },
      body: rawBody,
    }).catch(() => null);
    if (!res) return new Response('Upstream error', { status: 502 });
    // Mirror upstream status
    return new Response(await res.text(), { status: res.status });
  } catch (err: any) {
    return new Response(`Webhook Error: ${err?.message || 'invalid'}`, { status: 400 });
  }
}
