# Phase 5 – Stripe Webhooks für Credit-Gutschriften

Dieser Leitfaden beschreibt die Einrichtung des Stripe Webhooks im FastAPI-Backend, die Verarbeitung relevanter Events und Tests mit der Stripe CLI.

## Überblick

- Endpoint: `POST /webhooks/stripe`
- Signaturprüfung: mittels `STRIPE_WEBHOOK_SECRET` (Stripe-Signature Header)
- Unterstützte Events:
  - `checkout.session.completed`
  - `invoice.paid`
- Mapping:
  - Stripe `customer_id` → `clerk_user_id` via Tabelle `stripe_customers` (Fallback: `metadata.clerk_user_id`)
  - `price_id` → Credits über ENV-Mapping (siehe unten)
- Idempotenz: via UNIQUE-Index auf `credit_ledger.stripe_event_id`

## ENV-Variablen (Backend)

- `STRIPE_SECRET_KEY` – Server-Secret, um API und Webhook-Verifikation zu ermöglichen.
- `STRIPE_WEBHOOK_SECRET` – Secret für die Signaturprüfung.
- `DATABASE_URL` – Neon Postgres Verbindung.
- Preis→Credit-Mapping (mindestens eine Variante ausfüllen):
  - `STRIPE_PRICE_TO_CREDITS_JSON` – JSON-Objekt, z. B.: `{"price_abc":100,"price_def":500}`
  - oder Einzeln:
    - `STRIPE_PRICE_SMALL_ID`, `STRIPE_PRICE_SMALL_CREDITS`
    - `STRIPE_PRICE_MEDIUM_ID`, `STRIPE_PRICE_MEDIUM_CREDITS`
    - `STRIPE_PRICE_LARGE_ID`, `STRIPE_PRICE_LARGE_CREDITS`

## Registrierung des Webhooks

- Stripe Dashboard → Developers → Webhooks → Add endpoint
  - URL: `https://<render-service>/webhooks/stripe`
  - Events: `checkout.session.completed`, `invoice.paid`
- Das generierte Signing Secret in `STRIPE_WEBHOOK_SECRET` eintragen.

## Testen mit Stripe CLI

1) Installieren: https://docs.stripe.com/stripe-cli
2) Anmelden: `stripe login`
3) Events weiterleiten:

```bash
# Terminal 1: lokale Weiterleitung
stripe listen --forward-to http://127.0.0.1:8000/webhooks/stripe

# Terminal 2: Events triggern
stripe trigger checkout.session.completed
stripe trigger invoice.paid
```

Erwartungen:
- HTTP 200 vom Endpoint
- Ein neuer Eintrag im `credit_ledger` mit:
  - `clerk_user_id`
  - `delta` > 0 (abhängig vom `price_id` Mapping)
  - `reason` = `purchase:<price_id>` oder `purchase:multiple`
  - `stripe_event_id` = Event-ID
- Idempotenz: Gleiches Event erneut senden → kein zweiter Eintrag.

## Edge Cases

- Kein Mapping `customer_id` → `clerk_user_id` (und keine `metadata.clerk_user_id`):
  - Wird geloggt, Endpoint antwortet `{ok:true}` ohne Buchung (200).
- Unbekannte `price_id` (nicht im Mapping):
  - Wird geloggt, `{ok:true}` ohne Buchung (200).
- Fehler beim Schreiben (z. B. Unique-Verletzung):
  - Rollback, Log, `{ok:true}` (200).

## Hinweise

- Der rohe Request-Body wird zur Signaturprüfung verwendet.
- Preise/IDs sollten 1:1 zum Frontend passen (siehe `docs/stripe-products.md`).
- In Staging/Prod das Stripe Dashboard entsprechend konfigurieren und Secrets sicher setzen.
