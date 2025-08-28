"use client";

import { useEffect } from 'react';
import { ResumePreviewProvider } from '@/components/common/resume_previewer_context';
import { CreditsBadge } from '@/components/common/credits-badge';
import Link from 'next/link';
import { useUser, SignedIn, SignedOut, SignInButton } from '@clerk/nextjs';

function AuthHeader() {
  const { isLoaded } = useUser();
  // Render a stable skeleton to avoid sign-out→sign-in flicker during hydration
  if (!isLoaded) {
    return (
      <div className="inline-flex items-center gap-2 rounded-md border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 text-sm">
        <span className="h-4 w-24 rounded bg-zinc-700/60 animate-pulse" aria-hidden />
      </div>
    );
  }
  return (
    <>
      <SignedIn>
        <CreditsBadge />
      </SignedIn>
      <SignedOut>
        <SignInButton>
          <button className="rounded-md px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm">Sign in</button>
          </SignInButton>
      </SignedOut>
    </>
  );
}

export default function DefaultLayout({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').catch(() => {});
    }
  }, []);
  const hasClerk = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);
  return (
    <ResumePreviewProvider>
      <div className="sticky top-0 z-50 p-4 flex gap-3 justify-end items-center bg-zinc-950/80 backdrop-blur border-b border-zinc-800">
        <Link href="/billing" className="rounded-md px-3 py-1.5 bg-rose-700 hover:bg-rose-600 text-white text-sm">Billing</Link>
        {hasClerk ? <AuthHeader /> : null}
      </div>
      <main className="min-h-screen flex flex-col">{children}</main>
    </ResumePreviewProvider>
  );
}
