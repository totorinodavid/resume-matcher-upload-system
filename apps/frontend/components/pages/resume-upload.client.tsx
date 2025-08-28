"use client";
import React from 'react';
import BackgroundContainer from '@/components/common/background-container';
import FileUpload from '@/components/common/file-upload';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import { SignedIn, SignedOut, SignInButton } from '@clerk/nextjs';

export default function ResumeUploadPageClient() {
  const t = useTranslations('ResumeUploadPage');
  const pathname = usePathname();
  const parts = pathname.split('/').filter(Boolean);
  const locale = parts[0] || 'en';
  return (
    <BackgroundContainer className="min-h-screen" innerClassName="bg-zinc-950 overflow-auto p-10">
      <div className="w-full max-w-3xl mx-auto flex flex-col gap-10">
        <header className="space-y-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-[linear-gradient(to_right,theme(colors.sky.500),theme(colors.pink.400),theme(colors.violet.600))]">
            {t('title')}
          </h1>
          <p className="text-gray-300 leading-relaxed">
            {t('description')}
          </p>
          <p className="text-xs text-gray-500">
            {t('note')}
          </p>
        </header>
        <SignedIn>
          <section className="bg-gray-900/60 backdrop-blur-sm p-6 rounded-xl border border-gray-800 shadow-lg">
            <FileUpload />
          </section>
        </SignedIn>
        <SignedOut>
          <section className="bg-gray-900/60 backdrop-blur-sm p-6 rounded-xl border border-gray-800 shadow-lg text-center">
            <p className="text-gray-300 mb-4">Bitte zuerst anmelden, um deinen Lebenslauf hochzuladen.</p>
            <SignInButton mode="modal">
              <button className="px-4 py-2 rounded-md bg-white/10 hover:bg-white/20 text-white border border-white/20">
                Jetzt anmelden
              </button>
            </SignInButton>
          </section>
        </SignedOut>
        <div className="flex justify-center text-sm text-gray-400 gap-6">
          <Link href={`/${locale}`} className="hover:text-gray-200 underline underline-offset-4">{t('home')}</Link>
          <Link href={`/${locale}/dashboard`} className="hover:text-gray-200 underline underline-offset-4">{t('dashboard')}</Link>
        </div>
      </div>
    </BackgroundContainer>
  );
}
