"use client";

import { useEffect, useState } from 'react';
import { SignedIn, SignedOut, SignInButton, UserButton, useUser } from '@clerk/nextjs';
import { CreditProducts, type CreditPlan } from '@/lib/stripe/products';

async function createCheckout(price_id: string, credits?: number): Promise<string | null> {
  const res = await fetch('/api/stripe/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ price_id, credits }),
    credentials: 'include',
  });
  if (!res.ok) {
    let message = 'Checkout konnte nicht erstellt werden.';
    try {
      const data = await res.json();
      if (data?.error) message = String(data.error);
    } catch {}
    throw new Error(message);
  }
  const data = await res.json();
  return data?.url ?? null;
}

async function openPortal(): Promise<string | null> {
  const res = await fetch('/api/stripe/portal', { method: 'POST', credentials: 'include' });
  if (!res.ok) {
    let message = 'Portal konnte nicht erstellt werden.';
    try {
      const data = await res.json();
      if (data?.error) message = String(data.error);
    } catch {}
    throw new Error(message);
  }
  const data = await res.json();
  return data?.url ?? null;
}

export default function BillingPage() {
  const hasClerk = Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);
  const { isLoaded } = useUser();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [flash, setFlash] = useState<string | null>(null);

  const onBuy = async (plan: CreditPlan) => {
    setError(null);
    setLoading(plan.id);
    try {
  const url = await createCheckout(plan.price_id, plan.credits);
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

  // Detect Stripe success return to show feedback and ensure fresh balance fetch from backend
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const url = new URL(window.location.href);
      const status = url.searchParams.get('status');
      if (status === 'success') {
        setFlash('Kauf erfolgreich – Guthaben wird aktualisiert…');
        // Trigger a background refresh of the current balance endpoint used by the app
        fetch('/api/me/credits', { cache: 'no-store' }).catch(() => undefined);
        // Notify any mounted components using useCreditsState to refresh immediately
        window.dispatchEvent(new CustomEvent('credits:refresh'));
        // Clean query param to avoid repeating on rerenders
        url.searchParams.delete('status');
        window.history.replaceState({}, '', url.toString());
      }
    } catch {}
  }, []);

  // Avoid rendering auth-dependent UI until Clerk has hydrated to prevent login flicker
  if (hasClerk && !isLoaded) return null;

  return (
    <div className="mx-auto max-w-3xl p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Billing</h1>
        {hasClerk ? (<SignedIn><UserButton /></SignedIn>) : null}
      </div>

      {hasClerk ? (
        <SignedOut>
          <div className="rounded border p-4">
            <p className="mb-2">Optional anmelden für Portalzugang. Kauf von Credits ist auch ohne Login möglich.</p>
            <SignInButton>
              <button className="px-3 py-2 rounded bg-blue-600 text-white">Sign in</button>
            </SignInButton>
          </div>
        </SignedOut>
      ) : (
        <div className="rounded border p-4 text-sm text-gray-300">Portal erfordert Login. Du kannst Credits dennoch kaufen.</div>
      )}

      {error && <div className="text-sm text-red-600">{error}</div>}
  {flash && <div className="text-sm text-green-700">{flash}</div>}

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

      {hasClerk ? (
        <SignedIn>
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
      ) : null}
    </div>
  );
}
