# Stripe Produkte und Preis-IDs (Phase 4)

In Phase 4 verwenden wir eine reine Frontend-Integration für Stripe Checkout und das Billing Portal. Es gibt noch keine Webhooks oder serverseitige Gutschriftverbuchung.

## Produkte/Preise konfigurieren

Finale Pakete (Live):
- Basic – 50 Credits – 4,99€
- Pro – 200 Credits – 9,99€ (Most Popular)
- Ultimate – 1000 Credits – 24,99€ (Best Value)

Frontend (Vercel): Preis-IDs per ENV setzen – nur IDs, kein Credit-Mapping im Client
- NEXT_PUBLIC_STRIPE_PRICE_SMALL → Basic (Live price_id)
- NEXT_PUBLIC_STRIPE_PRICE_MEDIUM → Pro (Live price_id)
- NEXT_PUBLIC_STRIPE_PRICE_LARGE → Ultimate (Live price_id)

Backend (Render): Credits-Mapping zentral per ENV, idempotent über Webhook
- STRIPE_PRICE_TO_CREDITS_JSON (Beispiel):
	`{ "price_live_basic": 50, "price_live_pro": 200, "price_live_ultimate": 1000 }`
	Alternativ: STRIPE_PRICE_SMALL_ID/MEDIUM_ID/LARGE_ID mit STRIPE_PRICE_*_CREDITS.

## API Routen

- POST /api/stripe/checkout – erstellt eine Stripe Checkout Session für den gegebenen `price_id` und gibt `url` zurück.
- POST /api/stripe/portal – erstellt eine Billing Portal Session (temporär wird ein Kunde on-the-fly erzeugt).

Beide Routen laufen im Node.js Runtime-Kontext und verwenden `STRIPE_SECRET_KEY` (Server-Only!).

## .env Variablen (Frontend)

- STRIPE_SECRET_KEY: Secret Key (nur Server). Wird in den API Routes verwendet.
- NEXT_PUBLIC_STRIPE_PRICE_SMALL: Preis-ID für Basic.
- NEXT_PUBLIC_STRIPE_PRICE_MEDIUM: Preis-ID für Pro.
- NEXT_PUBLIC_STRIPE_PRICE_LARGE: Preis-ID für Ultimate.
- NEXT_PUBLIC_SITE_URL: Basis-URL für Success/Cancel Redirects (Fallback, optional).

## Hinweise

- Credits werden im Backend über den Webhook gutgeschrieben – nie im Client.
- Testen Sie mit Stripe Testkarten (4242 4242 4242 4242).
