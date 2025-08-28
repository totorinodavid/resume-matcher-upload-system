import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

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

export async function GET(req: NextRequest, ctx: any) {
  return proxy(req, ctx?.params);
}

export async function POST(req: NextRequest, ctx: any) {
  return proxy(req, ctx?.params);
}

export async function PUT(req: NextRequest, ctx: any) {
  return proxy(req, ctx?.params);
}

export async function PATCH(req: NextRequest, ctx: any) {
  return proxy(req, ctx?.params);
}

export async function DELETE(req: NextRequest, ctx: any) {
  return proxy(req, ctx?.params);
}

async function proxy(req: NextRequest, params: { path: string[] } | undefined) {
  // Only allow forwarding to /api/v1/*
  const joined = (params?.path ?? []).join('/');
  if (!joined.startsWith('api/v1/')) return NextResponse.json({ error: 'Forbidden' }, { status: 403 });

  const a = await auth();
  // Prefer a Clerk JWT Template for backend verification. Configure CLERK_JWT_TEMPLATE in env (e.g., "backend").
  // Default to the server-side JWT template name used by the backend ('backend').
  // Fallback: if template-based token is unavailable, try default session token (reduces 401s that look like logouts).
  const template = process.env.CLERK_JWT_TEMPLATE || process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE || 'backend';
  let token: string | null = null;
  try {
    token = await a.getToken({ template });
  } catch {}
  if (!token) {
    try { token = await a.getToken(); } catch {}
  }
  const url = `${BACKEND_BASE}/${joined}` + (req.nextUrl.search || '');
  // If this is a protected POST endpoint and there is no token, return 401 directly
  const isProtectedPost = req.method !== 'GET' && (
    joined.startsWith('api/v1/resumes/upload') ||
    joined.startsWith('api/v1/resumes/improve') ||
    joined.startsWith('api/v1/jobs/upload') ||
    joined.startsWith('api/v1/match') ||
    joined.startsWith('api/v1/auth')
  );
  if (isProtectedPost && !token) {
  return NextResponse.json({ detail: 'Missing bearer token' }, { status: 401 });
  }

  const headers = new Headers(req.headers);
  headers.delete('host');
  headers.delete('x-forwarded-host');
  headers.delete('x-forwarded-proto');
  headers.delete('content-length'); // Let node-fetch compute length for streamed body
  headers.set('accept', 'application/json');
  // If request already has an Authorization header, keep it; otherwise attach Clerk token
  if (!headers.has('authorization') && !headers.has('Authorization')) {
    if (token) headers.set('authorization', `Bearer ${token}`);
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
