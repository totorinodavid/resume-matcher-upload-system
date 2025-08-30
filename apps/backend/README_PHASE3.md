# Phase 3 – Backend (FastAPI on Render): Auth Guard, Webhook, Credits

This backend implements NextAuth.js JWT auth, a Stripe webhook to credit purchases, and credit APIs.

## Environment variables

Set these in your local `.env` and on Render:

- DATABASE_URL: Neon Postgres URL (sslmode=require)
- SESSION_SECRET_KEY: random string for SessionMiddleware
- NEXTAUTH_SECRET: e.g. your-nextauth-secret-key
- NEXTAUTH_URL: e.g. https://your-frontend-domain.com
- STRIPE_SECRET_KEY: sk_live_... or sk_test_...
- STRIPE_WEBHOOK_SECRET: whsec_... from Stripe dashboard

Optional:
- ALLOWED_ORIGINS: JSON array of allowed origins (default includes localhost)

## Endpoints

- GET /healthz → 200, DB check
- GET /api/v1/me/hello → returns { data: { user } } (requires Bearer NextAuth JWT; in tests, set DISABLE_AUTH_FOR_TESTS=1)
- GET /api/v1/me/credits → returns { data: { balance } }
- POST /api/v1/credits/debit → { delta, reason? } → returns new balance; 402 on insufficient credits
- POST /api/v1/use-credits → { units, ref? } alias of debit
- POST /webhooks/stripe → verifies signature, credits ledger idempotently for events (checkout.session.completed, invoice.paid)

## Local run

- Ensure Python 3.12+, create venv, install requirements.
- Set SYNC/ASYNC db URLs or DATABASE_URL; run Alembic upgrade to head.
- Start app (uvicorn via `serve.py`).

## Render deployment

- Connect repo, use Dockerfile at root (Render Blueprint `render.yaml` provided).
- PreDeploy runs Alembic upgrade; the app starts with `python /app/apps/backend/serve.py`.
- Set env vars: DATABASE_URL, SESSION_SECRET_KEY, NEXTAUTH_SECRET, NEXTAUTH_URL, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET.
- Webhook URL in Stripe: https://<render-service>/webhooks/stripe

## Notes

- Credits are event-sourced via tables `stripe_customers`, `credit_ledger` and view `v_credit_balance`.
- Idempotency: duplicate Stripe events are ignored by a partial unique index on `credit_ledger.stripe_event_id`.
- Debits lock the customer row (`FOR UPDATE`) to prevent overdrafts.
