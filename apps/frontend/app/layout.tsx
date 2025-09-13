import type { Metadata } from 'next';
import { Geist, Space_Grotesk } from 'next/font/google';
import './globals.css';
import { defaultLocale } from '../i18n';

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
  return (
    <html lang={defaultLocale} className="dark h-full" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width,initial-scale=1" />
        <meta name="theme-color" content="#0f172a" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icons/icon-192.png" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
      </head>
      <body className="h-full antialiased bg-gradient-to-br from-blue-950 via-zinc-900 to-purple-950 text-white font-sans">
        <div className="fixed -top-40 -left-40 w-96 h-96 rounded-full bg-blue-600/20 blur-3xl"></div>
        <div className="fixed top-0 right-0 w-80 h-80 rounded-full bg-purple-600/20 blur-3xl"></div>
        <div className="fixed -z-10 inset-0 bg-[url('/grid.svg')] bg-center opacity-5"></div>
        {children}
      </body>
    </html>
  );
}
