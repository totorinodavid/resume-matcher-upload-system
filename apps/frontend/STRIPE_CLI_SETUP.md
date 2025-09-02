# Stripe CLI Setup & Webhook Configuration Guide

## 📥 Stripe CLI Installation (Windows)

### Option 1: Direct Download
1. Gehe zu: https://github.com/stripe/stripe-cli/releases/latest
2. Download: `stripe_1.21.8_windows_x86_64.zip` (neueste Version)
3. Entpacke in einen Ordner (z.B. `C:\stripe\`)
4. Füge den Pfad zu PATH hinzu oder verwende den vollständigen Pfad

### Option 2: PowerShell Download (Automatisch)
```powershell
# Download und Installation
$url = "https://github.com/stripe/stripe-cli/releases/latest/download/stripe_1.21.8_windows_x86_64.zip"
$output = "$env:TEMP\stripe-cli.zip"
$extractPath = "$env:USERPROFILE\stripe-cli"

Invoke-WebRequest -Uri $url -OutFile $output
Expand-Archive -Path $output -DestinationPath $extractPath -Force
```

## 🔑 Stripe CLI Setup

### 1. Login zu Stripe
```bash
# Nach Installation:
stripe login

# Folge den Anweisungen im Browser
```

### 2. Webhook Forwarding starten
```bash
# Terminal 1: Webhook forwarding
stripe listen --forward-to localhost:3000/api/stripe/credits-webhook

# Output wird sein:
# Ready! Your webhook signing secret is whsec_xxx
# Kopiere diesen Secret!
```

### 3. Environment Variable setzen
```env
# Füge zu .env.local hinzu:
STRIPE_WEBHOOK_SECRET=whsec_1234567890abcdef...
```

## 🧪 Webhook Testing

### Test Events senden
```bash
# Terminal 2: Test Events
stripe trigger checkout.session.completed
stripe trigger charge.refunded

# Überprüfe Terminal 1 für Webhook Empfang
```

### Local Development Server
```bash
# Terminal 3: Next.js Development
cd apps/frontend
npm run dev -- --port 3000
```

## 📋 Verification Checklist

- [ ] Stripe CLI heruntergeladen und installiert
- [ ] `stripe login` erfolgreich
- [ ] Webhook forwarding läuft auf localhost:3000
- [ ] Webhook secret in .env.local gesetzt
- [ ] Test events werden erfolgreich empfangen
- [ ] Credit system reagiert auf webhook events

## 🎯 Expected Webhook Flow

1. **stripe trigger checkout.session.completed**
   - Webhook wird an `/api/stripe/credits-webhook` gesendet
   - System verarbeitet Checkout-Event  
   - Credits werden automatisch zum User hinzugefügt
   - Balance wird in Datenbank aktualisiert

2. **stripe trigger charge.refunded**
   - Refund webhook wird empfangen
   - Credits werden automatisch abgezogen
   - Refund-Transaction wird protokolliert

---

**Nach erfolgreichem Setup kannst du Stripe Checkout testen!**
