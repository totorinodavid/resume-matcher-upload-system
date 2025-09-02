# Stripe Webhook Setup Guide

## 🔗 Webhook Endpoint Konfiguration

### Schritt 1: Stripe Dashboard öffnen
1. Gehe zu [https://dashboard.stripe.com/test/webhooks](https://dashboard.stripe.com/test/webhooks)
2. Klicke auf "Add endpoint"

### Schritt 2: Endpoint URL eingeben
```
https://your-domain.com/api/stripe/credits-webhook
```
Für Development:
```
http://localhost:3000/api/stripe/credits-webhook
```

### Schritt 3: Events auswählen
Füge diese Events hinzu:
- `checkout.session.completed` ✅
- `checkout.session.async_payment_succeeded` ✅
- `charge.refunded` ✅
- `refund.created` ✅

### Schritt 4: Webhook Secret kopieren
Nach der Erstellung:
1. Klicke auf den erstellten Webhook
2. Gehe zu "Signing secret"
3. Klicke "Reveal" und kopiere den Wert
4. Füge ihn zu deiner .env.local hinzu:
```env
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 🧪 Development Testing mit Stripe CLI

### Installation (falls noch nicht installiert)
```bash
# Windows (Scoop)
scoop install stripe

# Windows (Direct Download)
# https://github.com/stripe/stripe-cli/releases/latest
```

### Setup für lokales Testing
```bash
# Login
stripe login

# Webhook forwarding starten
stripe listen --forward-to localhost:3000/api/stripe/credits-webhook

# In einem neuen Terminal: Test Events senden
stripe trigger checkout.session.completed
stripe trigger charge.refunded
```

## 📋 Verification Checklist

- [ ] Webhook endpoint in Stripe Dashboard erstellt
- [ ] Correct events selected (checkout.session.completed, etc.)
- [ ] Webhook secret in .env.local hinzugefügt
- [ ] Stripe CLI setup für lokales Testing
- [ ] Test events erfolgreich verarbeitet
