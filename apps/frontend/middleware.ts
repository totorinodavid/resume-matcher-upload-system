import createMiddleware from 'next-intl/middleware';
import { NextResponse } from 'next/server';
import { auth } from '@/auth';

const intlMiddleware = createMiddleware({
  locales: ['en', 'de'],
  defaultLocale: 'en',
  localePrefix: 'always'
});

export async function middleware(request: any) {
  // Handle internationalization
  const intlResponse = intlMiddleware(request);
  
  // Handle authentication for protected routes
  const { pathname } = request.nextUrl;
  
  // Skip middleware for API routes, static files, and Next.js internals
  if (
    pathname.startsWith('/api/') ||
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/favicon.ico') ||
    pathname.startsWith('/manifest.json') ||
    pathname.startsWith('/icons/') ||
    pathname.includes('.')
  ) {
    return intlResponse;
  }

  // For protected routes, check authentication
  if (pathname.includes('/dashboard') || pathname.includes('/billing')) {
    const session = await auth();
    if (!session) {
      const url = new URL('/en/login', request.url);
      return NextResponse.redirect(url);
    }
  }

  return intlResponse;
}

export const config = {
  matcher: [
    // Match all pathnames except for
    // - API routes
    // - _next (Next.js internals)
    // - _static (inside /public)
    // - all root files inside /public (e.g. /favicon.ico)
    '/((?!api|_next|_static|.*\\..*).*)'
  ]
};