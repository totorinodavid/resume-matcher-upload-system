# Production ENV Matrix

This matrix lists required environment variables, where to set them, and notes. Remove all test/sandbox keys before go-live.

Vercel (Frontend)
- NEXT_PUBLIC_API_BASE: https://<backend-domain> (Render)
- NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: Clerk publishable (prod)
- CLERK_SECRET_KEY: Clerk secret (server only, for server routes if needed)
- CLERK_JWT_TEMPLATE: backend (token template name used by BFF)
- NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: Stripe publishable (Live)
- STRIPE_SECRET_KEY: Stripe secret (Live, server-only; used only by Next.js server routes)
- NEXT_PUBLIC_STRIPE_PRICE_SMALL / MEDIUM / LARGE: price IDs (Live) for UI
- SENTRY_DSN_FRONTEND: Sentry DSN for frontend (optional)

Render (Backend)
- DATABASE_URL: Neon Postgres (prod). The app derives sync/async URLs automatically.
- CLERK_JWT_ISSUER: https://clerk.<region>.clerk.accounts.dev (prod issuer)
- CLERK_AUDIENCE: API audience expected in Clerk JWTs
- STRIPE_SECRET_KEY: Stripe secret (Live)
- STRIPE_WEBHOOK_SECRET: Live webhook signing secret
- STRIPE_PRICE_TO_CREDITS_JSON: optional JSON map { price_id: credits }
- STRIPE_PRICE_SMALL_ID / MEDIUM_ID / LARGE_ID and corresponding *_CREDITS (optional fallback)
- SENTRY_DSN_BACKEND: Sentry DSN for backend (optional)

Neon (Database)
- Create a dedicated prod database and role with least-privilege (no SUPERUSER).
- Enable PITR/branching policy as per plan. Keep a staging branch for pre-prod testing.

General
- Never expose secret keys to the browser. Only publish NEXT_PUBLIC_* on Vercel; others must be Server/Build secrets.
- Confirm removal of any leftover test keys in all environments.
