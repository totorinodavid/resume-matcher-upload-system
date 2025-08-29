## Auth tokens for backend (BFF)

If your backend verifies Clerk JWTs, ensure the BFF requests a verifiable token by setting a Clerk JWT template:


## Authentication

This app uses NextAuth v5 with Google only. Set the following env vars in the frontend:

```env
AUTH_SECRET= # e.g. openssl rand -base64 32
AUTH_GOOGLE_ID=
AUTH_GOOGLE_SECRET=
```

Login route: `/login`

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
