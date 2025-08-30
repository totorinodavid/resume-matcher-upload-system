# Production Environment Matrix

This matrix lists required environment variables, where to set them, and notes. Remove all test/sandbox keys before go-live.

Vercel (Frontend)
- NEXT_PUBLIC_API_BASE: https://<backend-domain> (Render)
- NEXTAUTH_SECRET: NextAuth.js secret key (prod)
- NEXTAUTH_URL: https://your-production-domain.com
- GOOGLE_CLIENT_ID: Google OAuth client ID (optional)
- GOOGLE_CLIENT_SECRET: Google OAuth client secret (optional)
- GITHUB_CLIENT_ID: GitHub OAuth client ID (optional)  
- GITHUB_CLIENT_SECRET: GitHub OAuth client secret (optional)
- NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: Stripe publishable (Live)
- STRIPE_SECRET_KEY: Stripe secret (Live, server-only; used only by Next.js server routes)
- NEXT_PUBLIC_STRIPE_PRICE_SMALL / MEDIUM / LARGE: price IDs (Live) for UI
- SENTRY_DSN_FRONTEND: Sentry DSN for frontend (optional)

Render (Backend)
- DATABASE_URL: Neon Postgres (prod). The app derives sync/async URLs automatically.
- NEXTAUTH_SECRET: NextAuth.js secret key (same as frontend)
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

Example (Render → Environment Variables)
- STRIPE_PRICE_TO_CREDITS_JSON = {"price_live_basic":50,"price_live_pro":200,"price_live_ultimate":1000}
- or:
	- STRIPE_PRICE_SMALL_ID=price_live_basic, STRIPE_PRICE_SMALL_CREDITS=50
	- STRIPE_PRICE_MEDIUM_ID=price_live_pro, STRIPE_PRICE_MEDIUM_CREDITS=200
	- STRIPE_PRICE_LARGE_ID=price_live_ultimate, STRIPE_PRICE_LARGE_CREDITS=1000
