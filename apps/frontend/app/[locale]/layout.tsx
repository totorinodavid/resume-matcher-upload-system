import type { ReactNode } from 'react';
import { NextIntlClientProvider } from 'next-intl';
import enMessages from '../../messages/en.json';
import deMessages from '../../messages/de.json';
import { LanguageSwitcher } from '@/components/common/language-switcher';
import { ResumePreviewProvider } from '@/components/common/resume_previewer_context';
import ServiceWorkerRegistrar from '@/components/common/sw-registrar';
const locales = ['en', 'de'];
import type { Metadata } from 'next';
import { auth } from "@/auth";
import { LogoutButton } from '@/components/logout-button';
import { CreditsBadge } from '@/components/common/credits-badge';
import Link from 'next/link';
import { SessionProvider } from 'next-auth/react';

interface LayoutParams { params: Promise<{ locale: string }> }

export async function generateMetadata({ params }: LayoutParams): Promise<Metadata> {
  const { locale } = await params;
  const loc = locales.includes(locale) ? locale : 'en';
  const site = process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, '') || 'https://example.com';
  const basePath = `/${loc}`;
  const canonical = `${site}${basePath}`;
  const metaByLocale: Record<string, { title: string; description: string }> = {
    en: { title: 'Resume Matcher', description: 'Optimize your resume' },
    de: { title: 'Resume Matcher', description: 'Optimiere deinen Lebenslauf' }
  };
  const meta = metaByLocale[loc] || metaByLocale.en;
  return {
    title: meta.title,
    description: meta.description,
    alternates: {
      canonical,
      languages: Object.fromEntries(locales.map((l: string) => [l, `${site}/${l}`]))
    },
    openGraph: {
      url: canonical,
      title: meta.title,
      description: meta.description,
      siteName: 'Resume Matcher',
      locale: loc,
      type: 'website'
    },
    twitter: {
      card: 'summary',
      title: meta.title,
      description: meta.description
    }
  };
}

export default async function LocaleLayout({ children, params }: { children: ReactNode; params: Promise<{ locale: string }> }) {
  const { locale } = await params;
  const loc = locales.includes(locale) ? locale : 'en';
  const messages = loc === 'de' ? deMessages : enMessages;
  const session = await auth();
  return (
    <SessionProvider session={session}>
      <NextIntlClientProvider messages={messages} locale={loc} timeZone="UTC">
        <ResumePreviewProvider>
          <ServiceWorkerRegistrar />
          <div className="sticky top-0 z-50 p-4 flex gap-3 justify-end items-center bg-zinc-950/80 backdrop-blur border-b border-zinc-800">
            <LanguageSwitcher />
            <Link href="/billing" className="rounded-md px-3 py-1.5 bg-rose-700 hover:bg-rose-600 text-white text-sm">Billing</Link>
            {session?.user ? (
              <>
                <CreditsBadge className="mr-2" />
                <LogoutButton />
                {(process.env.NODE_ENV !== 'production' || process.env.NEXT_PUBLIC_SHOW_DEBUG === '1') && (
                  <Link href="/api/bff/api/v1/auth/whoami" target="_blank" className="rounded-md px-2 py-1 text-xs text-zinc-300 hover:text-white underline">
                    WhoAmI
                  </Link>
                )}
              </>
            ) : (
              <>
                <Link href="/login" className="rounded-md px-3 py-1.5 bg-zinc-700 hover:bg-zinc-600 text-white text-sm">Sign in</Link>
              </>
            )}
          </div>
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              name: "Resume Matcher",
              applicationCategory: "BusinessApplication",
              operatingSystem: "Any",
              description: loc === 'de' ? 'Optimiere deinen Lebenslauf für ATS und Job Keywords.' : 'Optimize your resume for ATS and job keywords.',
              url: (process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com') + '/' + loc,
              inLanguage: loc,
              offers: { "@type": "Offer", price: "0", priceCurrency: "USD" }
            }) }}
          />
          <div className="w-full pt-2">{children}</div>
        </ResumePreviewProvider>
      </NextIntlClientProvider>
    </SessionProvider>
  );
}
