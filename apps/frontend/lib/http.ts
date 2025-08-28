// Central HTTP utility that attaches Clerk session token as Authorization: Bearer <token>
// Supports both Client Components (browser) and Server (server actions/route handlers)

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';

export interface HttpOptions extends RequestInit {
  method?: HttpMethod;
  query?: Record<string, string | number | boolean | undefined>;
  timeoutMs?: number;
  // When true (default), include Authorization header with Clerk token if available
  auth?: boolean;
}

const DEFAULT_TIMEOUT = 30000;

function buildUrl(input: string, query?: HttpOptions['query']): string {
  let url = input;
  if (query) {
    const qs = Object.entries(query)
      .filter(([, v]) => v !== undefined)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join('&');
    if (qs) url += (url.includes('?') ? '&' : '?') + qs;
  }
  return url;
}

async function getClerkToken(): Promise<string | null> {
  try {
    if (typeof window === 'undefined') {
      // Server-side: use @clerk/nextjs/server
      const { auth } = await import('@clerk/nextjs/server');
      const a = await auth();
      const template = process.env.CLERK_JWT_TEMPLATE || process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE || 'default';
      return (await a.getToken({ template })) || null;
    }
    // Client-side: try global Clerk instance first
    const anyWin: any = globalThis as any;
    const clerk = anyWin?.Clerk;
    if (clerk?.session?.getToken) {
      const template = process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE || 'default';
      const t = await clerk.session.getToken({ template }).catch(() => null);
      if (t) return t;
    }
    // Fallback: dynamic import and attempt to read getToken if available (older Clerk versions)
    const mod: any = await import('@clerk/nextjs').catch(() => ({}));
    const getToken = mod?.getToken as undefined | ((args?: any) => Promise<string | null>);
    if (typeof getToken === 'function') {
      return (await getToken({ template: process.env.NEXT_PUBLIC_CLERK_JWT_TEMPLATE || 'default' })) || null;
    }
    return null;
  } catch {
    return null;
  }
}

export async function httpFetch<T = unknown>(input: string, opts: HttpOptions = {}): Promise<T> {
  const { method = 'GET', query, timeoutMs = DEFAULT_TIMEOUT, auth = true, headers, ...init } = opts;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const url = buildUrl(input, query);
    const hdrs = new Headers(headers || {});
    if (auth && !hdrs.has('authorization')) {
      const token = await getClerkToken();
      if (token) hdrs.set('authorization', `Bearer ${token}`);
    }
    const res = await fetch(url, {
      method,
      headers: hdrs,
      credentials: 'include',
      cache: 'no-store',
      ...init,
      signal: controller.signal,
    });
    const ct = res.headers.get('content-type') || '';
    const isJson = ct.includes('application/json');
    if (!res.ok) {
      const body = isJson ? await res.json().catch(() => ({})) : await res.text().catch(() => '');
      const err: any = new Error('HTTP_ERROR');
      err.status = res.status;
      err.data = body;
      throw err;
    }
    return (isJson ? await res.json() : await res.text()) as T;
  } finally {
    clearTimeout(timer);
  }
}

// Convenience: build backend base URL (used by callers to construct absolute URLs when needed)
export function getBackendBase(): string {
  const backendDefault = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : 'https://resume-matcher-backend-j06k.onrender.com';
  return (process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || backendDefault).replace(/\/$/, '');
}
