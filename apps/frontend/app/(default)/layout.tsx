"use client";

import { useEffect } from 'react';
import { ResumePreviewProvider } from '@/components/common/resume_previewer_context';
import { CreditsBadge } from '@/components/common/credits-badge';
import Link from 'next/link';

export default function DefaultLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  }, []);
  return (
    <ResumePreviewProvider>
      <div className="sticky top-0 z-50 p-4 flex gap-3 justify-end items-center bg-zinc-950/80 backdrop-blur border-b border-zinc-800">
        <Link href="/billing" className="rounded-md px-3 py-1.5 bg-rose-700 hover:bg-rose-600 text-white text-sm">Billing</Link>
        <CreditsBadge />
      </div>
      <main className="min-h-screen flex flex-col">{children}</main>
    </ResumePreviewProvider>
  );
}
