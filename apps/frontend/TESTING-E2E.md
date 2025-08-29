# E2E Setup (Local & CI)

This project uses Playwright for frontend E2E, pytest for backend tests, Stripe CLI for payments/webhooks, and NextAuth (Google) for auth.

## Prereqs
- Node 20+, npm 10+
- Python 3.12+
- Stripe CLI installed and logged in (`stripe --version`)
- Valid test keys for Stripe

## Quick Start (Local)

```powershell
# From repo root
npm install
npm run install:frontend

# Start backend & frontend together (or use docker-compose)
npm run dev

# In another terminal, forward Stripe webhooks to Next.js proxy -> backend
stripe listen --events checkout.session.completed,invoice.paid --forward-to http://localhost:3000/api/stripe/webhook

# Run E2E (strict project)
cd apps/frontend
$env:NEXT_PUBLIC_ENABLE_SW='0'
$env:E2E_TEST_MODE='1'
$env:STRIPE_SECRET_KEY='sk_test_...'
$env:E2E_TEST_EMAIL='test@example.com'
$env:NEXT_PUBLIC_STRIPE_PRICE_SMALL='price_...'
$env:NEXT_PUBLIC_STRIPE_PRICE_MEDIUM='price_...'
$env:NEXT_PUBLIC_STRIPE_PRICE_LARGE='price_...'

npx playwright test -c playwright.config.ts --project=strict-chromium
```

## Docker Compose

```powershell
docker compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Postgres: localhost:5432 (resumematcher/resumematcher)

## CI (GitHub Actions)
- Workflow `.github/workflows/e2e.yml` installs Node/Python/Stripe CLI and runs strict tests headless.
- Put secrets into repo Actions secrets:
  - STRIPE_SECRET_KEY
  - NEXT_PUBLIC_STRIPE_PRICE_SMALL/MEDIUM/LARGE
  - E2E_TEST_EMAIL

## Notes
- Service Workers are disabled in E2E to avoid offline fallbacks.
- The strict test clicks these selectors:
  - Billing: `a.rounded-md:nth-child(2)`
  - Small plan purchase: `div.rounded:nth-child(1) > button:nth-child(5)`
- The test extracts the `cs_...` ID, retrieves the Checkout Session, and confirms the PaymentIntent with `pm_card_visa` via Stripe CLI.
