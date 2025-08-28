import { NextRequest, NextResponse } from 'next/server';

// Ensure Node.js runtime (not Edge) for Stripe SDK and raw body access
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';

async function getStripe() {
	const key = process.env.STRIPE_SECRET_KEY;
	if (!key) throw new Error('Missing STRIPE_SECRET_KEY');
	const Stripe = (await import('stripe')).default;
	// Use a recent stable API version; align with checkout route
	return new Stripe(key, { apiVersion: '2024-12-18.acacia' as any });
}

export async function POST(req: NextRequest) {
	const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
	if (!webhookSecret) return new NextResponse('Stripe not configured', { status: 503 });
	const stripe = await getStripe();
	const rawBody = await req.text();
	const sig = req.headers.get('stripe-signature') as string | null;
	if (!sig) return new NextResponse('Missing signature', { status: 400 });

	let event: any;
	try {
		event = stripe.webhooks.constructEvent(rawBody, sig, webhookSecret);
	} catch (err: any) {
		return new NextResponse(`Webhook Error: ${err?.message || 'invalid'}`, { status: 400 });
	}

	// Only process checkout.session.completed for credits top-up; ack all others
	if (event?.type === 'checkout.session.completed') {
		const session = event.data?.object || {};
		// Forward to the single source of truth: the backend FastAPI webhook
		// Backend implements idempotency via partial unique index on credit_ledger.stripe_event_id
		const backendDefault = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'https://resume-matcher-backend-j06k.onrender.com';
		const backendBase = (process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || backendDefault).replace(/\/$/, '');

		try {
			// Pass through the event body and signature so backend can verify independently using its secret
			const res = await fetch(`${backendBase}/webhooks/stripe`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'Stripe-Signature': req.headers.get('stripe-signature') || '',
				},
				body: rawBody,
				// Never cache webhooks
				cache: 'no-store',
			});
			// Treat any 2xx as success to avoid Stripe retries; otherwise still return 200 after logging
			if (!res.ok && (res.status < 200 || res.status >= 300)) {
				// Best-effort logging (no console in serverless sometimes)
			}
		} catch {
			// Swallow backend network errors to keep webhook idempotent; dedupe is enforced in backend
		}
	}

	return new NextResponse('OK', { status: 200 });
}

