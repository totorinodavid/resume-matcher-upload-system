"use client";

import clsx from 'clsx';
import { useUser, SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import { CreditsBadge } from '@/components/common/credits-badge';

interface Props { className?: string; showUserButton?: boolean }

export function AuthActions({ className, showUserButton = true }: Props) {
  const { isLoaded } = useUser();
  if (!isLoaded) {
    return (
      <div className={clsx('inline-flex items-center gap-2', className)}>
        <span className="h-4 w-24 rounded bg-zinc-700/60 animate-pulse" aria-hidden />
      </div>
    );
  }
  return (
    <div className={clsx('inline-flex items-center gap-2', className)}>
      <SignedIn>
        <CreditsBadge />
        {showUserButton ? <UserButton /> : null}
      </SignedIn>
      <SignedOut>
        <SignInButton>
          <button className="rounded-md px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm">Sign in</button>
        </SignInButton>
      </SignedOut>
    </div>
  );
}
