import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0;
export const fetchCache = 'force-no-store';
export const runtime = 'nodejs';
export const maxDuration = 120;

const defaultBackend = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000'
  : 'https://resume-matcher-backend-j06k.onrender.com';
const BACKEND_BASE = (process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || defaultBackend).replace(/\/$/, '');

export async function GET(req: NextRequest) { return proxy(req); }
export async function POST(req: NextRequest) { return proxy(req); }
export async function PUT(req: NextRequest) { return proxy(req); }
export async function PATCH(req: NextRequest) { return proxy(req); }
export async function DELETE(req: NextRequest) { return proxy(req); }

async function proxy(req: NextRequest) {
  const path = req.nextUrl.searchParams.get('path') || '';
  if (!path.startsWith('/api/')) return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  const url = BACKEND_BASE + path + (req.nextUrl.search || '').replace(/^\?path=[^&]*&?/, '?');

  const headers = new Headers(req.headers);
  headers.delete('host');
  headers.delete('x-forwarded-host');
  headers.delete('x-forwarded-proto');
  headers.delete('content-length');
  // Preserve incoming Authorization header 1:1
  const init: RequestInit & { duplex?: 'half' } = {
    method: req.method,
    headers,
    body: req.method === 'GET' || req.method === 'HEAD' ? undefined : (req.body as any),
    ...(req.method !== 'GET' && req.method !== 'HEAD' ? { duplex: 'half' as const } : {}),
    cache: 'no-store',
    redirect: 'manual',
  };
  try {
    const res = await fetch(url, init);
    return new NextResponse(res.body, { status: res.status, headers: res.headers });
  } catch (e: any) {
    return NextResponse.json({ error: 'BACKEND_UNREACHABLE', message: e?.message || String(e) }, { status: 502 });
  }
}
