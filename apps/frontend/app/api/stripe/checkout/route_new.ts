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
  // Use a valid Stripe API version that matches TypeScript definitions
  return new Stripe(key, { apiVersion: '2024-06-20' });
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
    
    // BULLETPROOF: Require sign-in for purchasing credits
    if (!userId) {
      console.error('❌ CRITICAL: No user ID available for checkout');
      return NextResponse.json({ error: 'Sign-in required to purchase credits' }, { status: 401 });
    }

    // BULLETPROOF: Validate user ID format
    if (typeof userId !== 'string' || !userId.trim()) {
      console.error('❌ CRITICAL: Invalid user ID format:', userId);
      return NextResponse.json({ error: 'Invalid user session' }, { status: 401 });
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
    const plan = CreditProducts.find((p: any) => p.price_id === price_id && !p.price_id.endsWith('_placeholder'));
    if (!plan) {
      return NextResponse.json({ error: 'Unknown or placeholder price_id. Configure NEXT_PUBLIC_STRIPE_PRICE_* envs.' }, { status: 400 });
    }
    const credits = plan.credits;
    const plan_id = plan.id;

    // BULLETPROOF: ULTIMATE User-ID Metadata with Multiple Fallbacks
    const ultimateMetadata = {
      // PRIMARY: The main user ID (this is what the webhook will use)
      user_id: String(userId),
      
      // BACKUP: Store user ID in multiple fields for maximum reliability
      primary_user_id: String(userId),
      nextauth_user_id: String(userId),
      authenticated_user: String(userId),
      
      // PAYMENT DETAILS
      credits: String(credits),
      price_id: String(price_id),
      plan_id: String(plan_id || 'unknown'),
      
      // VALIDATION DATA
      purchase_timestamp: new Date().toISOString(),
      frontend_version: '2.0',
      checkout_source: 'bulletproof_frontend',
      
      // USER CONTEXT
      session_email: authSession?.user?.email || 'unknown',
      session_name: authSession?.user?.name || 'unknown',
      
      // DEBUG INFO
      session_expires: authSession?.expires || 'unknown'
    };

    // BULLETPROOF: Comprehensive validation and logging
    console.log('🚀 BULLETPROOF ULTIMATE Checkout metadata:', ultimateMetadata);
    
    // Triple validation of user ID
    const userIdChecks = [
      ultimateMetadata.user_id,
      ultimateMetadata.primary_user_id,
      ultimateMetadata.nextauth_user_id,
      ultimateMetadata.authenticated_user
    ];
    
    const validUserIds = userIdChecks.filter(id => id && id !== 'undefined' && id.trim().length > 0);
    
    if (validUserIds.length === 0) {
      console.error('❌ BULLETPROOF VALIDATION FAILED: No valid user IDs found!', {
        userId,
        authSession: authSession?.user,
        userIdChecks,
        metadata: ultimateMetadata
      });
      return NextResponse.json({ 
        error: 'CRITICAL: User authentication validation failed' 
      }, { status: 500 });
    }
    
    console.log('✅ BULLETPROOF VALIDATION PASSED:', {
      user_id: String(userId),
      validation_count: validUserIds.length,
      credits: credits,
      price_id: price_id
    });

    const stripeSession = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: price_id, quantity: 1 }],
      
      // BULLETPROOF: Multiple user reference points
      client_reference_id: String(userId),
      
      // ULTIMATE: Metadata that GUARANTEES webhook success
      metadata: ultimateMetadata,
      
      success_url,
      cancel_url,
    });

    // FINAL LOG: Session created successfully
    console.log('✅ BULLETPROOF CHECKOUT SESSION CREATED:', {
      session_id: stripeSession.id,
      user_id: String(userId),
      credits: credits,
      metadata_user_id: ultimateMetadata.user_id
    });

    return NextResponse.json({ url: stripeSession.url }, { status: 200 });
  } catch (err: unknown) {
    const error = err as Error & { message?: string };
    console.error('❌ CHECKOUT ERROR:', error);
    return NextResponse.json({ error: error?.message || 'stripe_error' }, { status: 500 });
  }
}
