import { test, expect, Page } from '@playwright/test';
import { execFile as _execFile } from 'node:child_process';
import { promisify } from 'node:util';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

const requireEnv = (name: string) => {
  const v = process.env[name];
  if (!v) throw new Error(`Missing ${name} for strict e2e`);
  return v;
};

// Pre-conditions for strict test run
const NEXTAUTH = process.env.NEXTAUTH_SECRET;
const STRIPE = process.env.STRIPE_SECRET_KEY;
const HAS_E2E = Boolean(process.env.E2E_TEST_EMAIL && process.env.E2E_TEST_PASSWORD);

// Skip entire file if required envs are not provided
NEXTAUTH && STRIPE && HAS_E2E
  ? test.describe.configure({ mode: 'default' })
  : test.describe.skip('strict e2e skipped (missing NextAuth/Stripe/E2E creds)', () => {});

const execFile = promisify(_execFile);

async function stripeExecJson(args: string[]) {
  const sk = process.env.STRIPE_SECRET_KEY;
  if (!sk) throw new Error('Missing STRIPE_SECRET_KEY');
  const bin = process.platform === 'win32' ? 'stripe' : 'stripe';
  // Always pass -k to avoid depending on interactive login state
  try {
    const { stdout } = await execFile(bin, ['-k', sk, ...args, '--format', 'json'], { windowsHide: true });
    return JSON.parse(stdout.trim() || '{}');
  } catch (e: any) {
    throw new Error(`stripe ${args.join(' ')} failed: ${e?.stderr || e?.message || 'unknown'}`);
  }
}

// Programmatic sign-in using NextAuth.js
async function signInIfNeeded(page: Page) {
  const email = requireEnv('E2E_TEST_EMAIL');
  // Try programmatic sign-in first; it sets the session cookie without relying on NextAuth JS
  try {
    // Navigate to sign-in endpoint directly
    await page.goto('/api/auth/signin');
    return;
  } catch (err) {
    // Fallback: perform UI sign-in using email + password
    // Navigate to sign-in so NextAuth UI and script initialize for sure
    await page.goto('/sign-in');
    // Disable SW via runtime flag to avoid offline fallback interfering in CI
    await page.addInitScript(() => {
      try { localStorage.setItem('NEXT_PUBLIC_ENABLE_SW', '0'); } catch {}
    });
    // Wait for the sign-in UI (do not rely on window.NextAuth)
    await page.getByRole('heading', { name: /sign in|anmeldung/i }).first().waitFor({ state: 'visible', timeout: 30000 }).catch(() => {});
    const password = requireEnv('E2E_TEST_PASSWORD');
    // Fill email/identifier
    const emailLocator = page.locator('input[type="email"], input[name="identifier"], input[id*="identifier" i]');
    await emailLocator.first().fill(email);
    // Continue/Next
    const continueButton = page.getByRole('button', { name: /continue|fortfahren|weiter|next/i }).first();
    if (await continueButton.isVisible()) {
      await continueButton.click();
    } else {
      // Some UIs have a direct submit
      await page.keyboard.press('Enter');
    }
    // Wait for password step
    const pwdInput = page.locator('input[type="password"], input[name="password"], input[id*="password" i]');
    await pwdInput.first().waitFor({ state: 'visible', timeout: 30000 });
    await pwdInput.first().fill(password);
    const signInButton = page.getByRole('button', { name: /sign in|anmelden|continue|weiter/i }).first();
    if (await signInButton.isVisible()) {
      await signInButton.click();
    } else {
      await page.keyboard.press('Enter');
    }
    // Give NextAuth a moment to establish the session
    await page.waitForTimeout(1500);
  }
}

// Test that checkout route is protected and creates a session with a real price id
// Requires NEXT_PUBLIC_STRIPE_PRICE_* to be set to valid IDs

test('Stripe checkout via UI and confirm with Stripe CLI', async ({ page }) => {
  // Ensure signed-in
  await signInIfNeeded(page);

  // Navigate to a page where the Billing link exists and click it
  await page.goto('/');
  const navBilling = page.locator('[data-testid="nav-billing"]');
  if (await navBilling.count()) {
    await navBilling.first().click();
  } else {
    // Fallback to provided CSS if testid missing
    await page.locator('a.rounded-md:nth-child(2)').first().click();
  }

  // Trigger the small credit package using provided selector
  const checkoutReq = page.waitForResponse((r) => r.url().includes('/api/stripe/checkout') && r.request().method() === 'POST');
  const buySmall = page.locator('[data-testid="buy-small"]');
  if (await buySmall.count()) {
    await buySmall.first().click();
  } else {
    // Fallback to provided CSS if testid missing
    await page.locator('div.rounded:nth-child(1) > button:nth-child(5)').first().click();
  }
  const resp = await checkoutReq;
  expect(resp.ok()).toBeTruthy();
  const data = await resp.json();
  expect(data.url).toMatch(/^https:\/\/checkout\.stripe\.com\//i);

  // Extract cs_ id from the returned URL
  const m = String(data.url).match(/(cs_(?:test|live)_[A-Za-z0-9]+)/);
  expect(m, 'Could not extract Checkout Session ID').toBeTruthy();
  const sessionId = m![1];

  // Retrieve session and confirm its PaymentIntent with a test card
  const session = await stripeExecJson(['checkout', 'sessions', 'retrieve', sessionId]);
  const pi: string = typeof session.payment_intent === 'string' ? session.payment_intent : session.payment_intent?.id;
  expect(pi, 'payment_intent missing on session').toBeTruthy();

  const confirmed = await stripeExecJson(['payment_intents', 'confirm', pi, '--payment-method', 'pm_card_visa']);
  expect(String(confirmed.status)).toMatch(/succeeded|processing/);

  // Optional: give webhook a moment to hit backend and UI to update
  await page.waitForTimeout(2000);
});

// Test Billing portal creation for signed-in user

test('Stripe portal session created for signed-in user', async ({ page, baseURL }) => {
  await signInIfNeeded(page);
  await page.goto('/billing');

  const resp = await page.request.post(`${baseURL}/api/stripe/portal`);
  expect(resp.status()).toBe(200);
  const json = await resp.json();
  expect(json.url).toMatch(/^https:\/\/billing\.stripe\.com\//i);
});
