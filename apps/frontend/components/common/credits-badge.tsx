"use client";

import Link from 'next/link';
import { useCreditsState } from '@/hooks/useCredits';
import clsx from 'clsx';

interface Props { className?: string }

export function CreditsBadge({ className }: Props) {
  const { balance, loading, error, refresh } = useCreditsState();
  const label = loading
    ? 'Credits…'
    : typeof balance === 'number'
      ? `Credits: ${balance}`
      : 'Credits: —';
  const title = error ? `Fehler: ${error}` : 'Zu Billing wechseln';
  return (
    <Link
      href="/billing"
      title={title}
      className={clsx(
        'inline-flex items-center gap-2 rounded-md border border-zinc-700 bg-zinc-900/60 px-3 py-1.5 text-sm text-zinc-100 hover:bg-zinc-800',
        className,
      )}
      onClick={(e) => { /* allow navigation; also refresh in background */ setTimeout(() => refresh().catch(() => {}), 0); }}
    >
      <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" aria-hidden />
      <span>{label}</span>
    </Link>
  );
}
