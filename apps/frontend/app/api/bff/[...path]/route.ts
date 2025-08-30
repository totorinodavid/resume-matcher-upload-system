import { NextRequest, NextResponse } from 'next/server';
import { auth } from "@/auth";

// This route depends on per-request auth cookies. Disable static optimization/caching.
export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';
export const runtime = 'nodejs';
// Increase function timeout to accommodate long backend operations
export const maxDuration = 120;

// Whitelist the backend origin to avoid open proxy
const defaultBackend = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000'
  : 'https://resume-matcher-backend-j06k.onrender.com';
const BACKEND_BASE = (process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || defaultBackend).replace(/\/$/, '');

export async function GET(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return proxy(req, await ctx?.params);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return proxy(req, await ctx?.params);
}

export async function PUT(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return proxy(req, await ctx?.params);
}

export async function PATCH(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return proxy(req, await ctx?.params);
}

export async function DELETE(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  return proxy(req, await ctx?.params);
}

async function proxy(req: NextRequest, params: { path: string[] } | undefined) {
  // Only allow forwarding to /api/v1/*
  const joined = (params?.path ?? []).join('/');
  if (!joined.startsWith('api/v1/')) return NextResponse.json({ error: 'Forbidden' }, { status: 403 });

  const session = await auth();
  
  // Log session info for debugging (remove in production)
  console.log('BFF Proxy - Session check:', {
    hasSession: !!session,
    hasUser: !!session?.user,
    hasAccessToken: !!session?.accessToken,
    method: req.method,
    path: joined
  });

  const url = `${BACKEND_BASE}/${joined}` + (req.nextUrl.search || '');
  
  // Check if this is a protected endpoint that requires authentication
  const isProtectedEndpoint = 
    joined.startsWith('api/v1/resumes/upload') ||
    joined.startsWith('api/v1/resumes/improve') ||
    joined.startsWith('api/v1/jobs/upload') ||
    joined.startsWith('api/v1/match') ||
    joined.startsWith('api/v1/auth') ||
    (req.method !== 'GET' && joined.startsWith('api/v1/'));

  // For protected endpoints, require a session
  if (isProtectedEndpoint && !session?.user) {
    console.log('BFF Proxy - Authentication required but no session found');
    return NextResponse.json({ 
      error: 'AUTHENTICATION_REQUIRED',
      detail: 'Please sign in to access this resource' 
    }, { status: 401 });
  }

  const headers = new Headers(req.headers);
  headers.delete('host');
  headers.delete('x-forwarded-host');
  headers.delete('x-forwarded-proto');
  headers.delete('content-length'); // Let node-fetch compute length for streamed body
  headers.set('accept', 'application/json');
  
  // For authenticated requests, we can pass the user ID or email as a custom header
  // since we have a session but may not have a separate backend token
  if (session?.user) {
    // Pass user information to backend for identification
    headers.set('x-user-id', session.user.id || '');
    headers.set('x-user-email', session.user.email || '');
    headers.set('x-authenticated', 'true');
    
    // If we have an access token, use it as bearer token
    if (session.accessToken && typeof session.accessToken === 'string') {
      headers.set('authorization', `Bearer ${session.accessToken}`);
    }
  }

  const body = req.method === 'GET' || req.method === 'HEAD' ? undefined : (req.body as any);
  const init: RequestInit & { duplex?: 'half' } = {
    method: req.method,
    headers,
    body,
    // Required by Node 18+ when streaming a request body
    ...(body ? { duplex: 'half' as const } : {}),
    cache: 'no-store',
    redirect: 'manual',
  };

  let res: Response;
  try {
    res = await fetch(url, init);
  } catch (err: unknown) {
    // Surface backend connectivity issues clearly to the client
    console.error('BFF Proxy - Backend fetch failed:', err);
    return NextResponse.json(
      { error: 'BACKEND_UNREACHABLE', message: 'Failed to reach backend', detail: err instanceof Error ? err.message : String(err) },
      { status: 502 }
    );
  }
  const resHeaders = new Headers(res.headers);
  // Remove hop-by-hop headers
  resHeaders.delete('transfer-encoding');
  resHeaders.delete('connection');
  // Normalize JSON responses to avoid streaming quirks
  const respContentType = resHeaders.get('content-type') || '';
  if (respContentType.includes('application/json')) {
    // Read and re-send as JSON to ensure proper headers/body
    // Use text() then JSON.parse to avoid body-lock issues across runtimes
    const text = await res.text().catch(() => '');
    let data: any;
    try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }

    // Normalize credits balance shape for UX endpoints
    if (joined === 'api/v1/me/credits') {
      const normBalance = (
        typeof data?.data?.balance === 'number' ? data.data.balance
        : typeof data?.balance === 'number' ? data.balance
        : typeof data?.data?.credits === 'number' ? data.data.credits
        : typeof data?.credits === 'number' ? data.credits
        : null
      );
      data = { balance: normBalance, raw: data };
    }
    // Always serialize with a BigInt-safe replacer and send as plain JSON text
    const safeStringify = (value: unknown) => {
      try {
        return JSON.stringify(value, (_k, v) => (typeof v === 'bigint' ? v.toString() : v));
      } catch {
        // As a last resort, stringify a minimal wrapper
        return JSON.stringify({ ok: false });
      }
    };
    const bodyText = safeStringify(data ?? {});
    const outHeaders = new Headers({ 'content-type': 'application/json', 'cache-control': 'no-store' });
    return new NextResponse(bodyText, { status: res.status, headers: outHeaders });
  }
  // For non-JSON (should be rare), pass-through the body stream
  return new NextResponse(res.body, { status: res.status, headers: resHeaders });
}
