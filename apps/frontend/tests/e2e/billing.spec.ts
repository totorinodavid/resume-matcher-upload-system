import { test, expect } from '@playwright/test';

test('Billing page buttons exist and server routes respond', async ({ page }) => {
  await page.goto('/billing');
  await expect(page.getByRole('button', { name: /checkout|purchase/i })).toBeVisible({ timeout: 5000 });
  await expect(page.getByRole('button', { name: /portal|manage/i })).toBeVisible({ timeout: 5000 });
});
