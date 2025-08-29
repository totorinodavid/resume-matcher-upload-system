// Per requirement, export NextAuth middleware directly
export { auth as middleware } from '@/auth';

export const config = {
  // Protect everything except Next.js internals, static files, and favicon.ico
  matcher: ['/((?!_next|.*\\..*|favicon.ico).*)']
};
