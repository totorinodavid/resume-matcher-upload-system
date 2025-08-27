# Observability Setup

Sentry
- Frontend: set `SENTRY_DSN_FRONTEND` to enable Next.js integration (see next.config.ts).
- Backend: set `SENTRY_DSN_BACKEND` to enable FastAPI integration via ASGI middleware.

Vercel
- Use Project → Observability to view Function logs, Edge logs, and Errors.
  Docs: https://vercel.com/docs/observability

Render
- Service Logs show startup, requests, and errors. Configure Health Checks for readiness.
  Docs: https://render.com/docs/logs

OpenTelemetry (optional)
- Future: add OTel SDK for Python/Node to emit traces and metrics. Counters: `webhooks_processed_total`, `credits_debits_total`.
