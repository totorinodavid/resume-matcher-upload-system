import { test, expect } from '@playwright/test';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

const HAS_STRIPE = Boolean(process.env.STRIPE_SECRET_KEY);
const HAS_PRICE = Boolean(
  process.env.NEXT_PUBLIC_STRIPE_PRICE_SMALL ||
  process.env.NEXT_PUBLIC_STRIPE_PRICE_MEDIUM ||
  process.env.NEXT_PUBLIC_STRIPE_PRICE_LARGE
);

(HAS_STRIPE && HAS_PRICE
  ? test.describe
  : test.describe.skip)('strict ui billing flow (Stripe CLI forwarding)', () => {
  test('navigate to billing and click small package button', async ({ page, baseURL, context }) => {
    // Provide a synthetic user for API routes in E2E test mode
    const email = process.env.E2E_TEST_EMAIL || 'e2e@test.local';
  await context.addCookies([{ name: 'x-e2e-user', value: email, url: baseURL! }]);

  // Home → Billing using stable data-testid
  await page.goto('/');
  await page.getByTestId('nav-billing').click();

    // Wait for billing page to render plans
    await expect(page.getByRole('heading', { name: 'Billing' })).toBeVisible({ timeout: 15000 });
    // Click the buy button using stable data-testid if present, else fallback by text
    const smallTestId = page.getByTestId('buy-small');
    if (await smallTestId.count()) {
      await expect(smallTestId).toBeVisible({ timeout: 15000 });
      await smallTestId.click();
    } else {
      const btn = page.getByRole('button', { name: /credits kaufen/i }).first();
      await expect(btn).toBeVisible({ timeout: 15000 });
      await btn.click();
    }

    // Expect a redirect to Stripe Checkout to initiate
    await expect(page).toHaveURL(/https:\/\/checkout\.stripe\.com\//, { timeout: 30000 });
  });
});
