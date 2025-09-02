import { test, expect } from '@playwright/test';

test('Dashboard loads correctly', async ({ page }) => {
  await page.goto('/de/dashboard');
  // Basic dashboard test - just check it loads
  await expect(page).toHaveTitle(/Resume Matcher/);
});
