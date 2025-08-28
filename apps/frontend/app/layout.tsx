import type { Metadata } from 'next';
import { headers } from 'next/headers';
import { Geist, Space_Grotesk } from 'next/font/google';
import './globals.css';
import { locales, defaultLocale } from '../i18n';
import { ClerkProvider } from '@clerk/nextjs';
import Link from 'next/link';
import { AuthActions } from '@/components/common/auth-actions';

const _spaceGrotesk = Space_Grotesk({
  variable: '--font-space-grotesk',
  subsets: ['latin'],
  display: 'swap'
});

const _geist = Geist({
  variable: '--font-geist',
  subsets: ['latin'],
  display: 'swap'
});

export const metadata: Metadata = {
  title: 'Resume Matcher',
  description: 'Build your resume with Resume Matcher',
  applicationName: 'Resume Matcher',
  keywords: ['resume', 'matcher', 'job', 'application']
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // Server-side derive locale: prefer first path segment if valid, else Accept-Language, fallback default.
  // Next.js headers() returns a ReadonlyHeaders immediately; type confusion workaround with generics
  const h = headers() as unknown as Headers;
  // Read CSP nonce from middleware (if provided) to make Clerk work under strict CSP and in Private mode
  const nonce = h.get('x-nonce') || undefined;
  const pathname = h.get('x-invoke-path') || h.get('referer') || '/';
  const seg = pathname.split('/').filter(Boolean)[0];
  const localeList: readonly string[] = locales as readonly string[];
  let activeLocale: string | undefined = localeList.includes(seg) ? seg : undefined;
  if (!activeLocale) {
  const accept = h.get('accept-language');
    if (accept) {
      const preferred = accept.split(',').map((p: string) => p.split(';')[0].trim());
  activeLocale = preferred.find((p: string) => localeList.includes(p));
    }
  }
  if (!activeLocale) activeLocale = defaultLocale;
  const app = (
    <html lang={activeLocale} className="dark h-full" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <meta name="theme-color" content="#0f172a" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      </head>
      <body className="h-full antialiased bg-zinc-950 text-white font-sans">
        <div className="sticky top-0 z-50 p-4 flex gap-3 justify-end items-center bg-zinc-950/80 backdrop-blur border-b border-zinc-800">
          <Link href="/billing" className="rounded-md px-3 py-1.5 bg-rose-700 hover:bg-rose-600 text-white text-sm">Billing</Link>
          {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ? <AuthActions /> : null}
        </div>
        {children}
      </body>
    </html>
  );
  const pk = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  // If Clerk is configured, wrap the app with ClerkProvider (stable incognito with CSP nonce).
  // If not configured (e.g., local/static builds), render without Clerk to avoid build-time errors.
  return pk ? (
    <ClerkProvider
      publishableKey={pk}
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
      afterSignInUrl="/"
      afterSignUpUrl="/"
      nonce={nonce}
    >
      {app}
    </ClerkProvider>
  ) : app;
}
