import { NextRequest, NextResponse } from 'next/server';

// Node runtime required for Stripe signature verification downstream and raw body
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';
export const maxDuration = 30;

// We need the raw body to preserve the Stripe signature; do not parse JSON
export async function POST(req: NextRequest) {
  try {
    const sig = req.headers.get('stripe-signature') || req.headers.get('Stripe-Signature');
    if (!sig) return NextResponse.json({ error: 'Missing signature' }, { status: 400 });

    // Forward to backend webhook endpoint verbatim
    const backendDefault = process.env.NODE_ENV === 'development'
      ? 'http://localhost:8000'
      : 'https://resume-matcher-backend-j06k.onrender.com';
    const base = (process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || backendDefault).replace(/\/$/, '');

    const buf = await req.arrayBuffer();
    const res = await fetch(`${base}/webhooks/stripe`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Stripe-Signature': sig,
      },
      body: Buffer.from(buf),
    });

    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) {
      const data = await res.json().catch(() => ({}));
      return NextResponse.json(data, { status: res.status });
    }
    const text = await res.text().catch(() => '');
    return new NextResponse(text, { status: res.status });
  } catch (err: unknown) {
    const error = err as Error & { message?: string };
    return NextResponse.json({ error: error?.message || 'webhook_error' }, { status: 500 });
  }
}
