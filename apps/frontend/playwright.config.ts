import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';
dotenv.config({ path: '.env.local' });

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 90_000,
  globalSetup: './global.setup.ts',
  globalTeardown: './global.teardown.ts',
  webServer: {
    command: 'npm run dev',
    url: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    reuseExistingServer: false,
    timeout: 180_000,
    cwd: __dirname,
    env: {
      NEXT_PUBLIC_ENABLE_SW: '0',
      E2E_TEST_MODE: '1',
  NEXT_PUBLIC_E2E_TEST_MODE: '1',
  // No Clerk envs; NextAuth uses server actions and cookie session
      ...(process.env.STRIPE_SECRET_KEY ? { STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY } : {}),
      ...(process.env.NEXT_PUBLIC_STRIPE_PRICE_SMALL ? { NEXT_PUBLIC_STRIPE_PRICE_SMALL: process.env.NEXT_PUBLIC_STRIPE_PRICE_SMALL } : {}),
      ...(process.env.NEXT_PUBLIC_STRIPE_PRICE_MEDIUM ? { NEXT_PUBLIC_STRIPE_PRICE_MEDIUM: process.env.NEXT_PUBLIC_STRIPE_PRICE_MEDIUM } : {}),
      ...(process.env.NEXT_PUBLIC_STRIPE_PRICE_LARGE ? { NEXT_PUBLIC_STRIPE_PRICE_LARGE: process.env.NEXT_PUBLIC_STRIPE_PRICE_LARGE } : {}),
      ...(process.env.NEXT_PUBLIC_SITE_URL ? { NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL } : {}),
    },
  },
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    serviceWorkers: 'block',
    extraHTTPHeaders: {
      'x-e2e-user': process.env.E2E_TEST_EMAIL || 'e2e@test.local'
    },
  },
  projects: [
    // Smoke: default e2e, exclude strict tests
    { name: 'chromium', use: { ...devices['Desktop Chrome'] }, testMatch: ['**/*.spec.ts', '!**/*.strict.spec.ts'] },
    // Strict: only run *.strict.spec.ts when present
    { name: 'strict-chromium', use: { ...devices['Desktop Chrome'] }, testMatch: ['**/*.strict.spec.ts'] },
  ],
});
