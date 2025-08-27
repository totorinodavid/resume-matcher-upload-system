# Testing Strategy (Phase 7)

This project uses a layered testing strategy:

- Unit tests: business logic (services), query helpers, pure functions.
- Integration tests: FastAPI endpoints via httpx ASGI transport against a real Postgres (Neon) schema migrated by Alembic.
- E2E tests: Playwright for the Next.js app (auth flow, billing actions, dashboard balance and 402 flow).

Goals
- Verify credits ledger correctness: idempotent crediting, transactional debits, 402 on insufficient balance.
- Validate webhook signature handling and price→credits mapping.
- Ensure UI flows surface real balances and guide users to purchase when needed.

How to run
- Backend (requires Postgres URLs):
  - Set `ASYNC_DATABASE_URL=postgresql+asyncpg://...` and `SYNC_DATABASE_URL=postgresql+psycopg://...`.
  - Run: `pytest -q`
- Frontend E2E:
  - Install browsers: `npx playwright install --with-deps`
  - Run: `npx playwright test`

Notes
- Webhook tests stub Stripe signature verification and SDK usage where needed.
- For idempotency, send the same `stripe_event_id` twice and assert only one ledger entry impacts balance.
- For race conditions, fire two parallel debit requests and expect exactly one success.
