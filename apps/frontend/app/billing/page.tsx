"use client";

import { useState } from 'react';
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs';
import { CreditProducts, type CreditPlan } from '@/lib/stripe/products';

async function createCheckout(price_id: string): Promise<string | null> {
  const res = await fetch('/api/stripe/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ price_id }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  return data?.url ?? null;
}

async function openPortal(): Promise<string | null> {
  const res = await fetch('/api/stripe/portal', { method: 'POST' });
  if (!res.ok) return null;
  const data = await res.json();
  return data?.url ?? null;
}

export default function BillingPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onBuy = async (plan: CreditPlan) => {
    setError(null);
    setLoading(plan.id);
    try {
      const url = await createCheckout(plan.price_id);
      if (!url) throw new Error('Checkout konnte nicht erstellt werden.');
      window.location.href = url;
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(null);
    }
  };

  const onPortal = async () => {
    setError(null);
    setLoading('portal');
    try {
      const url = await openPortal();
      if (!url) throw new Error('Portal konnte nicht erstellt werden.');
      window.location.href = url;
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="mx-auto max-w-3xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Billing</h1>
        <SignedIn><UserButton /></SignedIn>
      </div>

      <SignedOut>
        <div className="rounded border p-4">
          <p className="mb-2">Bitte einloggen, um Credits zu kaufen und das Portal zu öffnen.</p>
          <SignInButton>
            <button className="px-3 py-2 rounded bg-blue-600 text-white">Sign in</button>
          </SignInButton>
        </div>
      </SignedOut>

      <SignedIn>
        {error && <div className="text-sm text-red-600">{error}</div>}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {CreditProducts.map((p: CreditPlan) => (
            <div key={p.id} className="rounded border p-4 space-y-2">
              <div className="text-lg font-semibold">{p.title}</div>
              <div className="text-3xl font-bold">{p.priceLabel}</div>
              <div className="text-sm text-gray-600">{p.credits} Credits</div>
              {p.benefits?.length ? (
                <ul className="text-sm list-disc pl-5 text-gray-700">
                  {p.benefits.map((b: string, i: number) => (<li key={i}>{b}</li>))}
                </ul>
              ) : null}
              <button
                className="w-full mt-2 px-3 py-2 rounded bg-rose-600 text-white"
                onClick={() => onBuy(p)}
                disabled={loading === p.id}
              >
                {loading === p.id ? 'Weiterleit…' : 'Credits kaufen'}
              </button>
            </div>
          ))}
        </div>

        <div className="rounded border p-4">
          <div className="mb-2">Verwalte deine Zahlungen & Rechnungen:</div>
          <button
            className="px-3 py-2 rounded bg-gray-800 text-white"
            onClick={onPortal}
            disabled={loading === 'portal'}
          >
            {loading === 'portal' ? 'Öffnet…' : 'Customer Portal öffnen'}
          </button>
        </div>
      </SignedIn>
    </div>
  );
}
