# Runbook (Operations & Support)

Payments
- Refunds: Process in Stripe Dashboard → Payments → Select charge → Refund. Docs: https://docs.stripe.com/refunds
- Disputes: Monitor Stripe Dashboard → Disputes. Collect evidence (receipts, logs of credit delivery) and submit before deadlines. Docs: https://docs.stripe.com/disputes

Credits
- Manual credit grant: use admin tooling or run a controlled SQL insert into `credit_ledger` with a clear `reason` (e.g., `manual_adjustment:<ticket#>`). Always reference the user’s `clerk_user_id`. Ensure auditing by recording who performed the action.
- Idempotency: webhook replays are safe; purchases use unique `stripe_event_id`.

Pricing
- To change pricing, create new Prices in Stripe (Live). Update mapping via `STRIPE_PRICE_TO_CREDITS_JSON` (or fallback envs). Do not reuse old price IDs.

Incidents
- Webhook failures: check backend logs (Render). Use Stripe Dashboard → Events to replay. Idempotent credits protect against duplicates.
- Backend outage: Render status; scale as needed. Frontend shows graceful error states.

Key rotation
- Rotate Stripe and Clerk keys per policy. Update Vercel/Render envs. Redeploy. Document change in CHANGELOG and runbook annotations.

Reporting
- Export reports in Stripe (Payouts, Balance, Charges). Docs: https://docs.stripe.com/reports

## Billing / Credits

- Webhook endpoint: POST /webhooks/stripe (FastAPI backend). Next.js /api/stripe/webhook forwards to backend.
- Idempotency: credit_ledger.stripe_event_id has a partial unique index. Re-delivery of the same Stripe event will not change balance.
- Balance view: v_credit_balance aggregates from credit_ledger.
- UI refresh: After successful checkout redirect, /billing triggers a background fetch of /api/me/credits and dispatches a credits:refresh event consumed by useCreditsState().
- Mapping: stripe_customers maps Stripe customer ids to Clerk clerk_user_id. Metadata clerk_user_id on checkout session is used as fallback.
