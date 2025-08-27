# Docs Index (Phase 7)

- TESTING: `docs/TESTING.md`
- LOGGING: `docs/LOGGING.md`
- OBSERVABILITY: `docs/OBSERVABILITY.md`
- SECURITY CHECKS: `docs/SECURITY_CHECKS.md`

Quick commands
- Backend: `pytest -q` (set Postgres env URLs)
- Frontend E2E: `npx playwright install --with-deps` then `npx playwright test`
- Stripe CLI: `stripe listen --forward-to http://localhost:8000/webhooks/stripe`; `stripe trigger checkout.session.completed`
