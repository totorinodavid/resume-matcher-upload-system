"use client";
import { useEffect } from 'react';

export default function ServiceWorkerRegistrar() {
  useEffect(() => {
    const isProd = process.env.NODE_ENV === 'production';
    const enabled = (process.env.NEXT_PUBLIC_ENABLE_SW ?? '1') !== '0';
    if (typeof window === 'undefined') return;
    if ('serviceWorker' in navigator) {
      if (isProd && enabled) {
        navigator.serviceWorker.register('/sw.js').catch(() => {});
      } else {
        // Ensure any previously installed SW is removed to avoid offline fallbacks in dev/tests
        navigator.serviceWorker.getRegistrations?.().then((regs) => {
          regs.forEach((r) => r.unregister().catch(() => {}));
        }).catch(() => {});
        // Best-effort clear caches created by the SW
        try {
          if (window.caches?.keys) {
            window.caches.keys().then((keys: string[]) => keys.forEach((k) => window.caches.delete(k))).catch(() => {});
          }
        } catch {}
      }
    }
  }, []);
  return null;
}
