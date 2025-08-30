# Release Process

Versioning & Changelog
- Tag releases (e.g., v0.1.0). Maintain a CHANGELOG with user-facing changes.
- Create Sentry releases with environment tags for frontend and backend. Docs: https://docs.sentry.io/product/releases/

CI gates
- Run unit/integration tests (pytest) and E2E (Playwright) in CI. Block production deploy on failures. Docs: https://playwright.dev/docs/ci
- Build Next.js and FastAPI images; run smoke checks.

Staged rollout
- Deploy to staging (separate Vercel/Render env + Neon branch). Validate:
  - Auth (NextAuth.js staging)
  - Checkout, Portal, Webhooks
  - Credits APIs and dashboard display
- Promote to prod after sign-off. Update DSNs/keys for production if different.

Post-release
- Monitor Vercel/Render logs and Sentry for errors.
- Run a small live test transaction and confirm ledger update and balance display.
