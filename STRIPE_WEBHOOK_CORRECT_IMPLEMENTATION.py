#!/usr/bin/env python3
"""
🔧 KORREKTE STRIPE WEBHOOK IMPLEMENTIERUNG
==========================================

Basierend auf offizieller Stripe-Dokumentation:
- https://stripe.com/docs/webhooks
- https://stripe.com/docs/webhooks/signatures
- https://stripe.com/docs/webhooks/quickstart

ERKENNTNISSE:
✅ Stripe signiert ALLE Webhooks (Test + Live)
✅ Signatur-Header: "Stripe-Signature"
✅ Raw Body erforderlich für Verifikation
✅ Zeitstempel-Toleranz: 5 Minuten (default)
✅ Environment-spezifische Secrets erforderlich

IMPLEMENTIERUNG:
1. Korrekte Signatur-Verifikation
2. Development-Bypass Option
3. Proper Error Handling  
4. Production-Ready Code
"""

import hmac
import hashlib
import time
import json
import requests
import os
from typing import Optional

def verify_stripe_signature(payload: str, sig_header: str, endpoint_secret: str, tolerance: int = 300) -> bool:
    """
    Verifiziere Stripe Webhook Signature gemäß offizieller Dokumentation
    
    Args:
        payload: Raw request body als String
        sig_header: Stripe-Signature Header Wert
        endpoint_secret: Webhook endpoint secret
        tolerance: Zeittoleranz in Sekunden (default: 5 Minuten)
    
    Returns:
        bool: True wenn Signatur gültig
    """
    try:
        # Parse signature header
        # Format: "t=timestamp,v1=signature"
        elements = sig_header.split(',')
        timestamp = None
        signature = None
        
        for element in elements:
            if element.startswith('t='):
                timestamp = int(element[2:])
            elif element.startswith('v1='):
                signature = element[3:]
        
        if timestamp is None or signature is None:
            print("❌ Ungültiger Stripe-Signature Header Format")
            return False
        
        # Check timestamp tolerance (Replay Attack Protection)
        current_time = int(time.time())
        if abs(current_time - timestamp) > tolerance:
            print(f"❌ Timestamp zu alt: {current_time - timestamp} Sekunden")
            return False
        
        # Compute expected signature
        payload_to_sign = f"{timestamp}.{payload}"
        expected_signature = hmac.new(
            endpoint_secret.encode('utf-8'),
            payload_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (secure comparison)
        if not hmac.compare_digest(signature, expected_signature):
            print("❌ Signatur-Verifikation fehlgeschlagen")
            return False
        
        print("✅ Stripe Signatur erfolgreich verifiziert")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Signatur-Verifikation: {e}")
        return False

def enhanced_webhook_handler(payload: str, headers: dict, endpoint_secret: Optional[str] = None) -> dict:
    """
    Enhanced Webhook Handler mit korrekter Signatur-Verifikation
    
    Args:
        payload: Raw request body
        headers: Request headers
        endpoint_secret: Webhook secret (optional für Development)
    
    Returns:
        dict: Response mit Status und Message
    """
    try:
        # 1. Parse JSON payload
        try:
            event_data = json.loads(payload)
        except json.JSONDecodeError as e:
            return {"status": 400, "error": f"Invalid JSON: {e}"}
        
        # 2. Signatur-Verifikation (wenn Secret vorhanden)
        if endpoint_secret:
            stripe_signature = headers.get('stripe-signature') or headers.get('Stripe-Signature')
            
            if not stripe_signature:
                return {"status": 400, "error": "Missing Stripe-Signature header"}
            
            if not verify_stripe_signature(payload, stripe_signature, endpoint_secret):
                return {"status": 400, "error": "Invalid signature"}
        else:
            print("⚠️ Development-Modus: Signatur-Verifikation übersprungen")
        
        # 3. Event Type prüfen
        event_type = event_data.get('type')
        if event_type != 'checkout.session.completed':
            return {"status": 200, "message": f"Ignored event type: {event_type}"}
        
        # 4. Extract Event Data
        checkout_session = event_data.get('data', {}).get('object', {})
        
        # 5. Extract Metadata
        metadata = checkout_session.get('metadata', {})
        user_id = metadata.get('user_id')
        credits = metadata.get('credits')
        
        if not user_id or not credits:
            return {"status": 400, "error": "Missing user_id or credits in metadata"}
        
        # 6. Credits hinzufügen (simuliert)
        print(f"🎉 CREDITS HINZUFÜGEN:")
        print(f"   User ID: {user_id}")
        print(f"   Credits: {credits}")
        print(f"   Payment Status: {checkout_session.get('payment_status')}")
        print(f"   Amount: {checkout_session.get('amount_total')}")
        
        # Hier würde normalerweise die Datenbank-Operation stattfinden
        # credits_service.add_credits(user_id, int(credits))
        
        return {
            "status": 200, 
            "message": "Credits successfully added",
            "data": {
                "user_id": user_id,
                "credits_added": credits,
                "event_id": event_data.get('id')
            }
        }
        
    except Exception as e:
        print(f"❌ Webhook Handler Error: {e}")
        return {"status": 500, "error": f"Internal error: {e}"}

def test_with_stripe_cli_style():
    """Test mit Stripe CLI ähnlicher Signatur"""
    print("🧪 TESTE MIT STRIPE CLI STYLE SIGNATUR...")
    
    # Simuliere Stripe CLI Webhook
    webhook_url = "https://resume-matcher-backend-j06k.onrender.com/"
    webhook_secret = "whsec_test_secret_from_cli"  # Von `stripe listen`
    
    # Stripe-konforme Payload
    payload = {
        "id": "evt_stripe_cli_test",
        "object": "event",
        "api_version": "2024-06-20",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_cli_test",
                "object": "checkout.session",
                "amount_total": 999,
                "currency": "eur",
                "payment_status": "paid",
                "status": "complete",
                "metadata": {
                    "user_id": "e747de39-1b54-4cd0-96eb-e68f155931e2",
                    "credits": "100"
                }
            }
        },
        "livemode": False,
        "type": "checkout.session.completed"
    }
    
    payload_string = json.dumps(payload, separators=(',', ':'))
    
    # Generate real Stripe signature
    timestamp = str(int(time.time()))
    payload_to_sign = f"{timestamp}.{payload_string}"
    
    signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    stripe_signature = f"t={timestamp},v1={signature}"
    
    headers = {
        "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        "Content-Type": "application/json",
        "Stripe-Signature": stripe_signature
    }
    
    print(f"📝 Generated Signature: {stripe_signature}")
    print(f"🚀 Testing webhook...")
    
    # Lokaler Test der Handler-Funktion
    response = enhanced_webhook_handler(
        payload=payload_string,
        headers=headers,
        endpoint_secret=webhook_secret
    )
    
    print(f"📊 Local Handler Result:")
    print(f"   Status: {response['status']}")
    print(f"   Response: {response}")
    
    # Test gegen live endpoint
    try:
        live_response = requests.post(
            webhook_url, 
            data=payload_string, 
            headers=headers, 
            timeout=20
        )
        
        print(f"\n🌐 Live Endpoint Result:")
        print(f"   Status: {live_response.status_code}")
        print(f"   Response: {live_response.text}")
        
        return live_response.status_code == 200
        
    except Exception as e:
        print(f"❌ Live test error: {e}")
        return False

def test_development_mode():
    """Test Development Mode ohne Signatur"""
    print("\n🧪 TESTE DEVELOPMENT MODE...")
    
    webhook_url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    payload = {
        "id": "evt_dev_test",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "payment_status": "paid",
                "metadata": {
                    "user_id": "e747de39-1b54-4cd0-96eb-e68f155931e2",
                    "credits": "100"
                }
            }
        }
    }
    
    payload_string = json.dumps(payload, separators=(',', ':'))
    
    headers = {
        "User-Agent": "Stripe/1.0",
        "Content-Type": "application/json"
        # Bewusst KEINE Stripe-Signature
    }
    
    # Lokaler Test ohne Secret
    local_response = enhanced_webhook_handler(
        payload=payload_string,
        headers=headers,
        endpoint_secret=None  # Development mode
    )
    
    print(f"📊 Development Mode Result:")
    print(f"   Status: {local_response['status']}")
    print(f"   Response: {local_response}")
    
    # Live test
    try:
        live_response = requests.post(
            webhook_url, 
            json=payload, 
            headers=headers, 
            timeout=15
        )
        
        print(f"\n🌐 Live Development Test:")
        print(f"   Status: {live_response.status_code}")
        print(f"   Response: {live_response.text}")
        
        return live_response.status_code == 200
        
    except Exception as e:
        print(f"❌ Development test error: {e}")
        return False

def production_requirements():
    """Production Deployment Requirements"""
    print("\n📋 PRODUCTION REQUIREMENTS:")
    print("=" * 50)
    
    print("1. 🔐 Environment Variables:")
    print("   STRIPE_WEBHOOK_SECRET=whsec_live_...")
    print("   STRIPE_PUBLISHABLE_KEY=pk_live_...")
    print("   STRIPE_SECRET_KEY=sk_live_...")
    
    print("\n2. 🎯 Webhook Endpoint Setup:")
    print("   URL: https://yourdomain.com/webhooks/stripe")
    print("   Events: checkout.session.completed")
    print("   API Version: 2024-06-20 (latest)")
    
    print("\n3. ⚙️ Backend Implementation:")
    print("   - Raw body parsing (no JSON middleware)")
    print("   - Stripe-Signature header extraction")
    print("   - Timestamp tolerance: 300 seconds")
    print("   - Secure signature comparison")
    
    print("\n4. 🚀 Deployment Checklist:")
    print("   □ HTTPS enabled")
    print("   □ Webhook secret configured")
    print("   □ Event types selected")
    print("   □ Error handling implemented")
    print("   □ Idempotency protection")
    print("   □ Logging configured")
    
    print("\n5. 🧪 Testing Strategy:")
    print("   - Stripe CLI: stripe listen --forward-to localhost:8000")
    print("   - Dashboard webhook testing")
    print("   - Event triggering: stripe trigger checkout.session.completed")
    print("   - Signature validation testing")

def main():
    print("🔧 KORREKTE STRIPE WEBHOOK IMPLEMENTIERUNG")
    print("=" * 60)
    
    print("📚 BASIEREND AUF OFFIZIELLER DOKUMENTATION:")
    print("✅ Alle Webhooks werden signiert (Test + Live)")
    print("✅ Stripe-Signature Header erforderlich")
    print("✅ Raw Body für Verifikation benötigt")
    print("✅ Zeitstempel-Toleranz für Replay-Schutz")
    
    # Tests ausführen
    cli_success = test_with_stripe_cli_style()
    dev_success = test_development_mode()
    
    # Production Guide
    production_requirements()
    
    print(f"\n📊 TEST ERGEBNISSE:")
    print(f"   Stripe CLI Style: {'✅' if cli_success else '❌'}")
    print(f"   Development Mode: {'✅' if dev_success else '❌'}")
    
    print(f"\n🎯 EMPFOHLENE NÄCHSTE SCHRITTE:")
    if not cli_success and not dev_success:
        print("1. 🔧 Backend Webhook-Code mit korrekter Signatur-Verifikation updaten")
        print("2. 🌐 Environment Variables für Webhook Secret setzen")
        print("3. 🧪 Stripe CLI für lokale Tests installieren")
        print("4. 📊 Dashboard Webhook Endpoint konfigurieren")
    elif dev_success:
        print("1. ✅ Development-Bypass funktioniert")
        print("2. 🔐 Für Production: Webhook Secret konfigurieren")
        print("3. 🧪 Stripe CLI für vollständige Tests verwenden")
    else:
        print("1. 🎉 Webhook Signatur-Verifikation funktioniert!")
        print("2. 🚀 Production-Deployment durchführen")
        print("3. 📊 Live-Testing mit echten Payments")

if __name__ == "__main__":
    main()
