import { spawnSync } from 'node:child_process';

export default async function globalTeardown() {
  // Kill backend if we started it
  const backendPid = (global as any).__BACKEND_PID__ as number | undefined;
  if (backendPid) {
    try {
      if (process.platform === 'win32') {
        spawnSync('taskkill', ['/PID', String(backendPid), '/T', '/F'], { stdio: 'ignore', shell: true });
      } else {
        process.kill(backendPid, 'SIGTERM');
      }
    } catch {}
  }
  // Kill Stripe listen process if present
  const stripePid = (global as any).__STRIPE_LISTEN_PID__ as number | undefined;
  if (stripePid) {
    try {
      if (process.platform === 'win32') {
        spawnSync('taskkill', ['/PID', String(stripePid), '/T', '/F'], { stdio: 'ignore', shell: true });
      } else {
        process.kill(stripePid, 'SIGTERM');
      }
    } catch {}
  }
}
