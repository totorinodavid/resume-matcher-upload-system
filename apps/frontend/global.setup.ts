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

  // Start backend for testing
  let backendProc: ReturnType<typeof spawn> | undefined;
  try {
    const repoRoot = path.resolve(__dirname, '..', '..');
    const backendEnv = {
      ...process.env,
      // In tests we use a test PostgreSQL database for consistency
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
    const tmpDir = path.join(process.cwd(), '.playwright-tmp');
    fs.mkdirSync(tmpDir, { recursive: true });
    fs.writeFileSync(path.join(tmpDir, 'backend_pid'), String(backendProc.pid ?? ''), 'utf8');

    // Wait for backend to be ready
    try {
      await waitForHttp('http://localhost:8000/healthz', 30000);
    } catch {
      // Fallback to legacy ping
      await waitForHttp('http://localhost:8000/api/v1/health/ping', 30000);
    }
  } catch (error) {
    console.error('Failed to start backend:', error);
  }

  // Expose PID for teardown
  if (backendProc) (global as any).__BACKEND_PID__ = backendProc.pid;
}
