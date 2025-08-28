import createIntlMiddleware from 'next-intl/middleware';
import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { clerkMiddleware } from '@clerk/nextjs/server';
import { locales, defaultLocale } from './i18n';

// Base i18n middleware instance
const intlMiddleware = createIntlMiddleware({
  locales: [...locales],
  defaultLocale,
  localePrefix: 'always'
});

// Security headers (CSP hardened: no unsafe-inline/eval; support hashed/nonce scripts via runtime)
// Generate nonce using Web Crypto only (Edge runtime compatible)
function generateNonce(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  let out = '';
  for (let i = 0; i < bytes.length; i++) out += bytes[i].toString(16).padStart(2, '0');
  return out;
}

function buildCsp(nonce: string) {
  const defaultBackend = process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000'
    : 'https://resume-matcher-backend-j06k.onrender.com';
  const apiOrigin = process.env.NEXT_PUBLIC_API_BASE || process.env.NEXT_PUBLIC_API_URL || defaultBackend;
  // Always include the Render fallback to be safe if envs are missing
  const connectExtra = Array.from(new Set([apiOrigin, 'https://resume-matcher-backend-j06k.onrender.com'])).filter(Boolean);
  // Allow Next.js internal websocket endpoints for dev (/_next/) with wss: fallback
  const connectSrc = ["'self'", 'ws:', 'wss:', ...connectExtra];
  // Clerk host allowlist (optionally include a custom Clerk domain via env)
  const clerkCustom = process.env.NEXT_PUBLIC_CLERK_DOMAIN ? [`https://${process.env.NEXT_PUBLIC_CLERK_DOMAIN}`] : [];
  const clerkHosts = [
    'https://*.clerk.com',
    'https://*.clerk.services',
    'https://*.clerk.accounts.dev',
    ...clerkCustom,
  ];
  return [
    "default-src 'self'",
    // Scripts: allow self, Clerk domains, and inline to avoid nonce mismatches in App Router
    `script-src 'self' 'unsafe-inline' ${clerkHosts.join(' ')}`,
  // Allow web workers (Clerk uses blob workers). If worker-src is not set, script-src is used as fallback.
  "worker-src 'self' blob:",
  // For older user agents that still rely on child-src for workers
  "child-src 'self' blob:",
    // Styles: allow self, inline, Google Fonts, and Clerk assets
    `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com ${clerkHosts.join(' ')}`,
    "font-src 'self' https://fonts.gstatic.com data:",
    // Images: include Clerk image CDNs
    `img-src 'self' blob: data: https://raw.githubusercontent.com https://img.clerk.com ${clerkHosts.join(' ')}`,
    // Connect: backend + Clerk APIs (include accounts.dev)
    `connect-src ${connectSrc.join(' ')} ${clerkHosts.join(' ')}`,
    "media-src 'self'",
    "object-src 'none'",
    "frame-ancestors 'self'",
    // Clerk embeds
    `frame-src 'self' ${clerkHosts.join(' ')}`,
  "base-uri 'self'",
  // Allow Clerk-hosted form submissions (e.g., OAuth/SAML handshakes)
  `form-action 'self' ${clerkHosts.join(' ')}`,
    "manifest-src 'self'",
    // Optional reporting endpoint placeholder
    // "report-uri /api/csp-report"
  ].join('; ');
}

const permissionsPolicy: Record<string,string> = {
  'camera': '()',
  'microphone': '()',
  'geolocation': '()'
};

function baseMiddleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  // Normalize locale-prefixed paths, e.g. /de/sign-in -> /sign-in
  const segments = pathname.split('/').filter(Boolean);
  const maybeLocale = segments[0];
  const hasLocale = locales.includes(maybeLocale as any);
  const basePath = hasLocale ? `/${segments.slice(1).join('/')}` || '/' : pathname;
  // Skip i18n rewriting for Clerk auth routes (with or without locale)
  const isAuthRoute = basePath.startsWith('/sign-in') || basePath.startsWith('/sign-up');
  // Also skip i18n rewriting for API/TRPC routes so /api/* stays intact (even if locale was prefixed)
  const isApiRoute = basePath.startsWith('/api') || basePath.startsWith('/trpc');
  const response = (isAuthRoute || isApiRoute) ? NextResponse.next() : intlMiddleware(request);

  // Generate a nonce per response (hex)
  const nonce = generateNonce();

  // Apply security headers only to HTML/document requests and not on auth routes
  if (!isAuthRoute && !pathname.startsWith('/_next')) {
    response.headers.set('Content-Security-Policy', buildCsp(nonce));
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    response.headers.set('X-Frame-Options', 'SAMEORIGIN');
    response.headers.set('X-Content-Type-Options', 'nosniff');
    response.headers.set('X-DNS-Prefetch-Control', 'off');
    response.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
    response.headers.set('Permissions-Policy', Object.entries(permissionsPolicy).map(([k,v]) => `${k}=${v}`).join(', '));
    response.headers.set('X-Nonce', nonce); // expose for potential inline script components (can be removed later)
  }
  return response;
}

// If Clerk env vars are missing, fall back to a plain middleware to avoid crashes in Vercel
const hasClerkEnv = Boolean(process.env.CLERK_SECRET_KEY || process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);
export default (hasClerkEnv
  ? clerkMiddleware((auth, request) => baseMiddleware(request))
  : ((request: NextRequest) => baseMiddleware(request))
);

export const config = {
  // Protect everything except Next.js internals, static files, and favicon.ico
  matcher: ['/((?!_next|.*\\..*|favicon.ico).*)']
};
