# Security & Configuration Checklist

Secrets & Envs
- STRIPE_SECRET_KEY: server-only (backend and Next.js server routes). Never expose on client.
- STRIPE_WEBHOOK_SECRET: set in backend; used to verify webhooks.
- DATABASE_URL: Neon Postgres; ensure correct drivers are derived to sync/async URLs.
- Clerk JWT: issuer and audience configured; BFF attaches token for backend auth.

Headers & CORS
- Backends allow only known origins (Vercel preview + production + localhost). Avoid `*` in production.
- Ensure cookies/sessions use SameSite and secure in production.

Least Privilege
- Neon role should be limited (no superuser). Only CRUD on app schema.
- Rotate keys periodically.

Backups/Recovery
- Neon PITR (Point-in-Time-Recovery) available on paid plans. Document RPO/RTO expectations.
