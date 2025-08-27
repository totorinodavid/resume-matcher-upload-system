# Logging & Observability

Backend (FastAPI)
- Use structured, consistent logs. Include: `user_id` (if available), `route`, `status`, `latency_ms`, `request_id`.
- Sensitive data: never log PII (emails, phone numbers). A redaction filter is already attached to the root logger.
- Error tracking: enable Sentry by setting `SENTRY_DSN_BACKEND` and optional `SENTRY_TRACES_SAMPLE_RATE`.

Frontend (Next.js)
- Log only non-sensitive context. Never log raw resume/job content or emails.
- Surface important errors to Sentry (see Sentry setup in frontend).

Platforms
- Vercel: use Project → Observability to review function logs and errors.
- Render: check Service Logs and Health. Configure alerts for restarts and error spikes.

Metrics (optional)
- Consider OpenTelemetry counters (e.g., `webhooks_processed_total`) and gauges for queue sizes if background jobs are added later.
