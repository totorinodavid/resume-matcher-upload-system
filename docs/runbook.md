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
