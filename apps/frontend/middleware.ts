import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { auth } from "@/auth";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip auth checks for static files, API routes, and auth routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') ||
    pathname.includes('/login') ||
    pathname.includes('/logout')
  ) {
    return NextResponse.next();
  }

  // Protected routes that require authentication
  const protectedRoutes = ['/resume', '/dashboard'];
  const isProtectedRoute = protectedRoutes.some(route => pathname.includes(route));

  if (isProtectedRoute) {
    try {
      const session = await auth();
      
      if (!session) {
        // Extract locale from pathname (e.g., /en/resume -> en)
        const pathSegments = pathname.split('/').filter(Boolean);
        const locale = pathSegments[0] || 'en';
        const loginUrl = new URL(`/${locale}/login`, request.url);
        
        return NextResponse.redirect(loginUrl);
      }
    } catch (error) {
      console.error('Auth middleware error:', error);
      // Fallback to login on auth errors
      const pathSegments = pathname.split('/').filter(Boolean);
      const locale = pathSegments[0] || 'en';
      const loginUrl = new URL(`/${locale}/login`, request.url);
      
      return NextResponse.redirect(loginUrl);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
