"use client";

import { useEffect } from 'react';
import { ResumePreviewProvider } from '@/components/common/resume_previewer_context';
import Link from 'next/link';
// Note: Session-aware header exists in [locale]/layout.tsx; keep default layout minimal.

function AuthHeader() {
  return <Link href="/login" className="rounded-md px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm">Sign in</Link>;
}

export default function DefaultLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const isProd = process.env.NODE_ENV === 'production';
    const enabled = (process.env.NEXT_PUBLIC_ENABLE_SW ?? '1') !== '0';
    if (isProd && enabled && typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  }, []);
  return (
    <ResumePreviewProvider>
      <div className="sticky top-0 z-50 p-4 flex gap-3 justify-end items-center bg-zinc-950/80 backdrop-blur border-b border-zinc-800">
        <Link href="/billing" data-testid="nav-billing" className="rounded-md px-3 py-1.5 bg-rose-700 hover:bg-rose-600 text-white text-sm">Billing</Link>
        <AuthHeader />
      </div>
      <main className="min-h-screen flex flex-col">{children}</main>
    </ResumePreviewProvider>
  );
}
