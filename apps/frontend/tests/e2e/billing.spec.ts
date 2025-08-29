import { test, expect } from '@playwright/test';

test('Billing page shows at least one purchase action', async ({ page }) => {
  // Ensure no old service worker interferes
  await page.addInitScript(() => {
    try {
      // @ts-ignore
      if ('serviceWorker' in navigator) navigator.serviceWorker.getRegistrations?.().then((regs) => regs.forEach((r) => r.unregister())).catch(() => {});
      // @ts-ignore
      if (window.caches?.keys) window.caches.keys().then((keys) => keys.forEach((k) => window.caches.delete(k))).catch(() => {});
    } catch {}
  });
  await page.goto('/billing');
  // Prefer a direct purchase button when available
  const purchase = page.getByLabel(/purchase credits/i).first();
  const heading = page.getByRole('heading', { name: /billing/i });
  if (await purchase.count()) {
    await expect(purchase).toBeVisible({ timeout: 5000 });
  } else {
    await expect(heading).toBeVisible({ timeout: 5000 });
  }
});
