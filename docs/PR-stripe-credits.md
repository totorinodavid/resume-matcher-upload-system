# PR: Instant Stripe Credits Booking and Fresh UI Balance

Summary:
- Hardened checkout session metadata (clerk_user_id, credits) in Next.js.
- Added Next.js Node webhook `/api/stripe/webhook` with raw-body signature verification; forwards to backend for idempotent DB booking.
- Disabled backend alias `/api/stripe/webhook` to avoid duplicate processing.
- Backend webhook now respects `metadata.credits` if provided, otherwise maps price→credits.
- Added optional `stripe_events` table and env docs.
- UI refreshes balance on success return from Stripe without reload.

How it works:
1) Checkout → `/api/stripe/checkout` creates a session with metadata `{ clerk_user_id, credits? }`.
2) Stripe calls Vercel webhook `/api/stripe/webhook` → verifies signature and forwards payload to Render backend `/webhooks/stripe`.
3) FastAPI webhook verifies again, resolves Clerk user, books credits via `credit_ledger` with unique `stripe_event_id` (idempotent), commits.
4) Success redirect sets `status=success`; Billing page triggers a fresh fetch of `/api/me/credits` to update the badge/state.

Env:
- STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, NEXT_PUBLIC_SITE_URL, NEXT_PUBLIC_API_BASE
- Optionally STRIPE_PRICE_TO_CREDITS_JSON mapping.

Stripe CLI (local):
```
stripe listen --forward-to http://localhost:3000/api/stripe/webhook
stripe trigger checkout.session.completed
```

Acceptance checks:
- Webhook 200 on event.
- `credit_ledger` row created; `v_credit_balance` reflects delta.
- UI shows increased balance on success page without reload.
- Retries do not duplicate due to unique index on `credit_ledger.stripe_event_id`.
