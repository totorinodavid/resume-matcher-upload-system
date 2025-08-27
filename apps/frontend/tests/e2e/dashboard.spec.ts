import { test, expect } from '@playwright/test';

test('Dashboard shows a balance widget', async ({ page }) => {
  await page.goto('/de/dashboard');
  await expect(page.getByText(/Credits?/i)).toBeVisible();
});

test('Not enough credits flow shows CTA to buy', async ({ page }) => {
  await page.goto('/de/dashboard');
  // Try the demo action if present
  const btn = page.getByRole('button', { name: /Use 1 credit|Verbrauche 1 Credit/i });
  if (await btn.isVisible()) {
    await btn.click();
    // Expect either a notification or navigation hint to billing
    // Soft assertion: presence of link/button to billing
    const billingLink = page.getByRole('link', { name: /Billing|Kaufen|Purchase/i });
    await expect(billingLink).toBeVisible({ timeout: 5000 });
  }
});
