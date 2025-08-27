# Stripe Produkte und Preis-IDs (Phase 4)

In Phase 4 verwenden wir eine reine Frontend-Integration für Stripe Checkout und das Billing Portal. Es gibt noch keine Webhooks oder serverseitige Gutschriftverbuchung.

## Produkte/Preise konfigurieren

Legen Sie in Stripe drei Preise an (oder passen Sie die Anzahl an) und tragen Sie die Price-IDs in die Umgebungsvariablen ein:

- NEXT_PUBLIC_STRIPE_PRICE_SMALL
- NEXT_PUBLIC_STRIPE_PRICE_MEDIUM
- NEXT_PUBLIC_STRIPE_PRICE_LARGE

Diese werden vom UI unter `apps/frontend/lib/stripe/products.ts` gelesen.

## API Routen

- POST /api/stripe/checkout – erstellt eine Stripe Checkout Session für den gegebenen `price_id` und gibt `url` zurück.
- POST /api/stripe/portal – erstellt eine Billing Portal Session (temporär wird ein Kunde on-the-fly erzeugt).

Beide Routen laufen im Node.js Runtime-Kontext und verwenden `STRIPE_SECRET_KEY` (Server-Only!).

## .env Variablen (Frontend)

- STRIPE_SECRET_KEY: Secret Key (nur Server). Wird in den API Routes verwendet.
- NEXT_PUBLIC_STRIPE_PRICE_SMALL: Preis-ID für Small Paket.
- NEXT_PUBLIC_STRIPE_PRICE_MEDIUM: Preis-ID für Medium Paket.
- NEXT_PUBLIC_STRIPE_PRICE_LARGE: Preis-ID für Large Paket.
- NEXT_PUBLIC_SITE_URL: Basis-URL für Success/Cancel Redirects (Fallback, optional).

## Hinweise

- Diese Phase vergibt noch keine Credits automatisch. Das erfolgt in der nächsten Phase über Webhooks/Backend.
- Testen Sie mit Stripe Testkarten (4242 4242 4242 4242).
