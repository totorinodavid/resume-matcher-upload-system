"use client";
import { useCallback, useEffect, useState } from 'react';
import { getCreditsBalance, useCredits } from '@/lib/api/client';

export function useCreditsState() {
  const [balance, setBalance] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getCreditsBalance() as any;
      // Normalize various possible shapes into a single number
      const val = (
        typeof res?.data?.balance === 'number' ? res.data.balance
        : typeof res?.balance === 'number' ? res.balance
        : typeof res?.data?.credits === 'number' ? res.data.credits
        : typeof res?.credits === 'number' ? res.credits
        : null
      );
      setBalance(val ?? 0);
    } catch (e: any) {
      const msg = e?.message || 'Failed to load balance';
      // Common case: not signed in or backend proxy 401
      if (/401|unauthorized|Missing bearer token/i.test(msg)) {
        setError('Bitte anmelden, um dein Credits-Guthaben zu sehen.');
      } else if (/BACKEND_UNREACHABLE/i.test(msg)) {
        setError('Backend nicht erreichbar. Bitte später erneut versuchen.');
      } else {
        setError(msg);
      }
      setBalance(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  // Allow other pages (e.g., billing) to request a balance refresh without coupling
  useEffect(() => {
    const handler = () => { void refresh(); };
    if (typeof window !== 'undefined') {
      window.addEventListener('credits:refresh', handler as EventListener);
    }
    return () => {
      if (typeof window !== 'undefined') {
        window.removeEventListener('credits:refresh', handler as EventListener);
      }
    };
  }, [refresh]);

  const consume = useCallback(async (units: number, ref?: string) => {
    const res = await useCredits({ units, ref });
    if (res?.data?.ok) await refresh();
    return res;
  }, [refresh]);

  return { balance, loading, error, refresh, consume };
}
