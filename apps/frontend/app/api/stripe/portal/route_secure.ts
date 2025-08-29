import { NextRequest, NextResponse } from 'next/server';
import { auth } from "@/auth";

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';
export const maxDuration = 30;

/**
 * SECURITY HARDENING: Stripe Portal via Backend
 * 
 * BEFORE: Stripe Secret Key direkt im Frontend (UNSICHER!)
 * AFTER: Alle Stripe-Operationen im Backend, Frontend nur Proxy
 * 
 * Diese Route ruft die sichere Backend-API auf und leitet weiter.
 */
export async function POST(req: NextRequest) {
  try {
    const authSession = await auth();
    let userId = authSession?.user?.id;
    
    // E2E Test Support
    if (!userId && (process.env.E2E_TEST_MODE === '1' || process.env.E2E_TEST_MODE === 'true')) {
      const e2eUser = req.headers.get('x-e2e-user') || req.cookies.get('x-e2e-user')?.value;
      if (e2eUser) userId = e2eUser;
    }
    
    if (!userId) {
      return NextResponse.json({ error: 'Authentication required' }, { status: 401 });
    }
    
    const origin = req.headers.get('origin') || process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';
    const body = await req.json().catch(() => ({}));
    const return_url = body.return_url || `${origin}/billing`;
    
    // Sichere Backend-API aufrufen (über BFF)
    const backendUrl = `${origin}/api/bff/api/v1/billing/portal/create`;
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cookie': req.headers.get('cookie') || '', // Auth-Cookies weiterleiten
      },
      body: JSON.stringify({ return_url }),
      cache: 'no-store',
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Backend error' }));
      return NextResponse.json(
        { error: error.error?.message || 'Failed to create portal session' }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    
    // Nur die URL zurückgeben, wie die ursprüngliche API
    return NextResponse.json({ 
      url: data.data?.url 
    }, { status: 200 });
    
  } catch (err: any) {
    console.error('Portal creation error:', err);
    return NextResponse.json({ 
      error: err?.message || 'Internal server error' 
    }, { status: 500 });
  }
}
