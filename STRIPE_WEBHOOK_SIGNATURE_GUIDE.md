# 🔐 STRIPE WEBHOOK SIGNATURE GUIDE
## Korrekte Signaturprüfung für Test- und Live-Modus

### ❌ MEIN FEHLER - KORREKTUR:
**Stripe signiert ALLE Webhooks** - sowohl Test- als auch Live-Events haben echte Signaturen!

### 🔍 WARUM UNSERE TESTS FEHLSCHLAGEN:

1. **Selbst konstruierte Payloads haben keine echte Stripe-Signatur**
2. **Wir verwenden fake Signatures: `"t=123,v1=test"`**
3. **Stripe erwartet ECHTE Signaturen mit korrektem HMAC-SHA256**

---

## 🧪 KORREKTE TEST-IMPLEMENTIERUNG

### 1. **ECHTE STRIPE TEST-EVENTS VERWENDEN**

```bash
# ✅ Stripe CLI für echte Test-Events
stripe listen --forward-to localhost:8000/
stripe trigger checkout.session.completed

# ✅ Stripe Dashboard Test-Events  
# https://dashboard.stripe.com/test/webhooks -> Send test webhook
```

### 2. **LOKALE SIGNATUR-VALIDIERUNG BYPASSEN (Entwicklung)**

```python
# apps/backend/app/api/router/webhooks.py

async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    # ENTWICKLUNGS-MODUS: Signatur-Bypass für lokale Tests
    if os.getenv("STRIPE_WEBHOOK_BYPASS_SIGNATURE") == "true":
        logger.warning("⚠️ DEVELOPMENT: Bypassing Stripe signature validation")
        try:
            event = json.loads(payload.decode('utf-8'))
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from e
    else:
        # PRODUCTION: Echte Signatur-Validierung
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        try:
            if stripe is None:
                raise ImportError("Stripe module not available")
            
            if settings.STRIPE_SECRET_KEY:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature") from e
        except Exception as e:
            logger.exception("Stripe webhook parse error")
            raise HTTPException(status_code=400, detail="Invalid payload") from e
    
    # Webhook verarbeitung...
```

### 3. **ECHTE STRIPE-SIGNATUR GENERIEREN (Test-Tool)**

```python
# test_stripe_signature.py
import hmac
import hashlib
import time
import json

def generate_stripe_signature(payload_json: str, webhook_secret: str) -> str:
    """Generiere echte Stripe-Signatur für Tests"""
    timestamp = str(int(time.time()))
    
    # Stripe signature format: t=timestamp,v1=signature
    payload_to_sign = f"{timestamp}.{payload_json}"
    
    signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"t={timestamp},v1={signature}"

# Verwendung:
payload = json.dumps({
    "id": "evt_test",
    "type": "checkout.session.completed",
    "data": {"object": {"metadata": {"user_id": "test", "credits": "100"}}}
})

webhook_secret = "whsec_test_secret"
real_signature = generate_stripe_signature(payload, webhook_secret)
print(f"Real Stripe Signature: {real_signature}")
```

---

## 🔧 VOLLSTÄNDIGE WEBHOOK-FIX IMPLEMENTIERUNG

### 1. **ENVIRONMENT VARIABLE SETUP**

```bash
# Development (.env)
STRIPE_WEBHOOK_SECRET="whsec_test_..." # Test webhook secret
STRIPE_WEBHOOK_BYPASS_SIGNATURE="false" # Für echte Validierung

# Lokale Tests ohne Stripe CLI
STRIPE_WEBHOOK_BYPASS_SIGNATURE="true" # NUR für Development!

# Production
STRIPE_WEBHOOK_SECRET="whsec_live_..." # Live webhook secret  
STRIPE_WEBHOOK_BYPASS_SIGNATURE="false" # NIEMALS true in Production!
```

### 2. **ENHANCED WEBHOOK IMPLEMENTATION**

```python
# Enhanced webhook mit debugging
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    """Enhanced Stripe webhook mit korrekter Signatur-Handling"""
    
    # Configuration validation
    if not settings.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=503, detail="Webhook not configured")

    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    # Log webhook attempt (ohne sensitive Daten)
    logger.info(f"Stripe webhook received - has_signature: {bool(sig_header)}")
    
    # Development bypass (NIEMALS in Production!)
    bypass_signature = os.getenv("STRIPE_WEBHOOK_BYPASS_SIGNATURE", "false").lower() == "true"
    is_production = os.getenv("ENV", "development") == "production"
    
    if bypass_signature and is_production:
        logger.error("🚨 SECURITY: Signature bypass attempted in production!")
        raise HTTPException(status_code=500, detail="Security violation")
    
    if bypass_signature and not is_production:
        logger.warning("⚠️ DEVELOPMENT: Bypassing Stripe signature validation")
        try:
            event = json.loads(payload.decode('utf-8'))
            logger.info(f"Bypass mode - Event type: {event.get('type')}")
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload") from e
    else:
        # Production-grade signature validation
        if not sig_header:
            logger.error("Missing Stripe-Signature header")
            raise HTTPException(status_code=400, detail="Missing signature")
        
        try:
            if stripe is None:
                raise ImportError("Stripe module not available")
            
            # Set API key for additional context
            if settings.STRIPE_SECRET_KEY:
                stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Construct event with signature validation
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )
            logger.info(f"Signature verified - Event: {event['type']}")
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe signature verification failed: {e}")
            logger.error(f"Expected secret starts with: {settings.STRIPE_WEBHOOK_SECRET[:10]}...")
            raise HTTPException(status_code=400, detail="Invalid signature") from e
        except Exception as e:
            logger.exception("Stripe webhook parsing error")
            raise HTTPException(status_code=400, detail="Invalid payload") from e
    
    # Process webhook event
    try:
        result = await process_stripe_event(event, db)
        logger.info(f"Webhook processed successfully: {result}")
        return {"status": "success", "processed": result}
    except Exception as e:
        logger.exception(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Processing failed") from e
```

---

## 🧪 KORREKTE TEST-STRATEGIEN

### 1. **STRIPE CLI TESTING**

```bash
# ✅ Beste Methode: Stripe CLI
stripe login
stripe listen --forward-to https://resume-matcher-backend-j06k.onrender.com/
stripe trigger checkout.session.completed --add checkout_session:metadata[user_id]=test-user --add checkout_session:metadata[credits]=100
```

### 2. **STRIPE DASHBOARD TESTING**

```bash
# ✅ https://dashboard.stripe.com/test/webhooks
# 1. Select webhook endpoint
# 2. Click "Send test webhook"
# 3. Choose "checkout.session.completed"
# 4. Add metadata: user_id, credits
# 5. Send webhook -> ECHTE SIGNATUR!
```

### 3. **DEVELOPMENT BYPASS TESTING**

```python
# test_webhook_development.py
import requests
import json
import os

def test_development_webhook():
    """Test mit signature bypass für Development"""
    
    # Set bypass mode
    os.environ["STRIPE_WEBHOOK_BYPASS_SIGNATURE"] = "true"
    os.environ["ENV"] = "development"
    
    webhook_url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    payload = {
        "id": "evt_dev_test",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {
                    "user_id": "e747de39-1b54-4cd0-96eb-e68f155931e2",
                    "credits": "100"
                }
            }
        }
    }
    
    headers = {
        "User-Agent": "Stripe/1.0",
        "Content-Type": "application/json",
        # NO Stripe-Signature für bypass test
    }
    
    response = requests.post(webhook_url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_development_webhook()
```

---

## 🎯 SOFORTIGE KORREKTUR

**Möchtest du, dass ich:**

1. **✅ Den Webhook-Code mit korrekter Signatur-Validierung update?**
2. **✅ Ein Development-Bypass-System implementiere?**
3. **✅ Ein Tool für echte Stripe-Signatur-Generierung erstelle?**
4. **✅ Stripe CLI Test-Setup dokumentiere?**

**Du hast absolut recht - meine Annahme über Test-Mode Signaturen war falsch!**

**Soll ich das sofort korrigieren und eine vollständige Lösung implementieren?** 🔧
