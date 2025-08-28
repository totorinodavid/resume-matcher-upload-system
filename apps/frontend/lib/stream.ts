// Small streaming utilities for browser-side consumption of API route streams

export function fetchWithTimeout(url: string, options: RequestInit = {}, ms = 60_000) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), ms);
  return fetch(url, { ...options, signal: controller.signal, cache: 'no-store', credentials: 'include' })
    .finally(() => clearTimeout(t));
}

export async function readTextStream(res: Response, onChunk: (t: string) => void) {
  const reader = res.body?.getReader();
  if (!reader) return;
  const dec = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    if (value) onChunk(dec.decode(value, { stream: true }));
  }
}

// Simple client-side request de-duplication: prevents double-submit from onClick+onSubmit or StrictMode
const inFlightKeys = new Set<string>();
export async function dedup<T>(key: string, fn: () => Promise<T>): Promise<T> {
  if (inFlightKeys.has(key)) throw new Error('DUPLICATE_REQUEST');
  inFlightKeys.add(key);
  try { return await fn(); } finally { inFlightKeys.delete(key); }
}
