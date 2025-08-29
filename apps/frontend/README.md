## Auth (NextAuth.js)

This frontend uses NextAuth.js for authentication with Google OAuth.

### Environment Variables

To run the frontend locally, you need to set up the following environment variables in a `.env.local` file in this directory (`apps/frontend`):

```bash
# A random string used to hash tokens, sign cookies and generate cryptographic keys.
# You can generate one with `openssl rand -base64 32`
AUTH_SECRET=

# Google OAuth credentials
AUTH_GOOGLE_ID=
AUTH_GOOGLE_SECRET=
```

You can get Google OAuth credentials from the [Google API Console](https://console.developers.google.com/apis/credentials). Make sure to add `http://localhost:3000` to the "Authorized JavaScript origins" and `http://localhost:3000/api/auth/callback/google` to the "Authorized redirect URIs".

# UI

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## Stripe (Phase 4)

Server-Only API Routes:
- POST /api/stripe/checkout { price_id }
- POST /api/stripe/portal

UI:
- /billing – wählt Paket und startet Checkout; öffnet Customer Portal

ENV Variablen (Frontend):
- STRIPE_SECRET_KEY (Server Only)
- NEXT_PUBLIC_STRIPE_PRICE_SMALL
- NEXT_PUBLIC_STRIPE_PRICE_MEDIUM
- NEXT_PUBLIC_STRIPE_PRICE_LARGE
- NEXT_PUBLIC_SITE_URL (optional)

Details siehe `docs/stripe-products.md`.

## E2E Tests (Playwright)

Install browsers first:

```bash
npx playwright install --with-deps
```

Run tests:

```bash
npm run e2e
```
