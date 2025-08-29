// Central HTTP utility. With NextAuth, session is cookie-based; we don't attach Authorization by default.

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';

export interface HttpOptions extends RequestInit {
  method?: HttpMethod;
  query?: Record<string, string | number | boolean | undefined>;
  timeoutMs?: number;
  // Reserved for future use if bearer auth is added
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

async function getBearerToken(): Promise<string | null> { return null; }

export async function httpFetch<T = unknown>(input: string, opts: HttpOptions = {}): Promise<T> {
  const { method = 'GET', query, timeoutMs = DEFAULT_TIMEOUT, auth = true, headers, ...init } = opts;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const url = buildUrl(input, query);
    const hdrs = new Headers(headers || {});
  // With cookie session, no Authorization header is needed.
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
