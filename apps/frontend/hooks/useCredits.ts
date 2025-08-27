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
      const res = await getCreditsBalance();
      setBalance(res?.data?.balance ?? 0);
    } catch (e: any) {
      setError(e?.message || 'Failed to load balance');
      setBalance(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const consume = useCallback(async (units: number, ref?: string) => {
    const res = await useCredits({ units, ref });
    if (res?.data?.ok) await refresh();
    return res;
  }, [refresh]);

  return { balance, loading, error, refresh, consume };
}
