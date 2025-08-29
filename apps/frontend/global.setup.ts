import * as dotenv from 'dotenv';
import { spawn, spawnSync } from 'node:child_process';
import * as path from 'node:path';
import * as fs from 'node:fs';
import http from 'node:http';

async function waitForHttp(url: string, timeoutMs = 30000): Promise<void> {
  const started = Date.now();
  const tryOnce = () =>
    new Promise<void>((resolve, reject) => {
      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode < 500) resolve();
        else reject(new Error(`HTTP ${res.statusCode}`));
      });
      req.on('error', reject);
      req.setTimeout(2000, () => {
        req.destroy(new Error('timeout'));
      });
    });
  // retry loop
  // eslint-disable-next-line no-constant-condition
  while (true) {
    try {
      await tryOnce();
      return;
    } catch {
      if (Date.now() - started > timeoutMs) throw new Error(`Timeout waiting for ${url}`);
      await new Promise((r) => setTimeout(r, 500));
    }
  }
}

export default async function globalSetup() {
  // Load local envs for dev runs
  dotenv.config({ path: '.env.local' });
  // Disable SW during tests to avoid offline fallback
  process.env.NEXT_PUBLIC_ENABLE_SW = '0';
  // No Clerk mapping needed after migration to NextAuth

  // Try to integrate Stripe CLI for webhook forwarding if available
  let stripeListenProc: ReturnType<typeof spawn> | undefined;
  let backendProc: ReturnType<typeof spawn> | undefined;
  try {
    const ver = spawnSync('stripe', ['--version'], { encoding: 'utf8' });
    if (ver.status === 0) {
      // 1) Get ephemeral webhook signing secret
      const secretOut = spawnSync('stripe', ['listen', '--print-secret'], { encoding: 'utf8' });
      const webhookSecret = (secretOut.stdout || '').trim();
      if (webhookSecret && webhookSecret.startsWith('whsec_')) {
        // Persist for teardown & child processes
        process.env.STRIPE_WEBHOOK_SECRET = webhookSecret;
        const tmpDir = path.join(process.cwd(), '.playwright-tmp');
        fs.mkdirSync(tmpDir, { recursive: true });
        fs.writeFileSync(path.join(tmpDir, 'stripe_webhook_secret'), webhookSecret, 'utf8');

        // 2) Start long-running forwarder to Next.js webhook proxy (frontend forwards to backend)
        stripeListenProc = spawn('stripe', ['listen', '--forward-to', 'http://localhost:3000/api/stripe/webhook'], {
          stdio: 'inherit',
          env: { ...process.env },
          shell: process.platform === 'win32',
        });
        // Track PID for teardown
        fs.writeFileSync(path.join(tmpDir, 'stripe_listen_pid'), String(stripeListenProc.pid ?? ''), 'utf8');

        // 3) Start backend with the webhook secret in env so signature verification succeeds
        const repoRoot = path.resolve(__dirname, '..', '..');
        const backendEnv = {
          ...process.env,
          STRIPE_WEBHOOK_SECRET: webhookSecret,
          // Surface STRIPE_SECRET_KEY if present in .env.local
          ...(process.env.STRIPE_SECRET_KEY ? { STRIPE_SECRET_KEY: process.env.STRIPE_SECRET_KEY } : {}),
          // In tests we don't need Postgres; backend defaults to SQLite for tests
          DISABLE_BACKGROUND_TASKS: 'true',
          E2E_TEST_MODE: '1',
          DISABLE_AUTH_FOR_TESTS: '1',
        } as NodeJS.ProcessEnv;
        backendProc = spawn('npm', ['run', 'dev:backend'], {
          cwd: repoRoot,
          env: backendEnv,
          stdio: 'inherit',
          shell: process.platform === 'win32',
        });
        fs.writeFileSync(path.join(tmpDir, 'backend_pid'), String(backendProc.pid ?? ''), 'utf8');

        // 4) Wait for backend to be ready
        try {
          await waitForHttp('http://localhost:8000/healthz', 30000);
        } catch {
          // Fallback to legacy ping
          await waitForHttp('http://localhost:8000/api/v1/health/ping', 30000);
        }
      }
    }
  } catch {
    // Stripe CLI not available – continue without webhook forwarding
  }

  // Expose PIDs for teardown
  if (stripeListenProc) (global as any).__STRIPE_LISTEN_PID__ = stripeListenProc.pid;
  if (backendProc) (global as any).__BACKEND_PID__ = backendProc.pid;
}
