#!/usr/bin/env python3
"""
🔧 STRIPE WEBHOOK SIGNATURE FIX
===============================

KORREKTUR: Stripe signiert ALLE Webhooks (Test + Live)

PROBLEM: Unsere Tests verwenden fake Signaturen
LÖSUNG: Echte Signatur-Generierung oder Development-Bypass

IMPLEMENTIERUNG:
1. Enhanced webhook mit korrekter Signatur-Validierung
2. Development bypass für lokale Tests  
3. Echte Signatur-Generator für Tests
4. Stripe CLI integration guide
"""

import hmac
import hashlib
import time
import json
import requests
import os

def generate_real_stripe_signature(payload_string: str, webhook_secret: str) -> str:
    """Generiere ECHTE Stripe-Signatur für Tests"""
    timestamp = str(int(time.time()))
    
    # Stripe signature format: t=timestamp,v1=signature
    payload_to_sign = f"{timestamp}.{payload_string}"
    
    signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"t={timestamp},v1={signature}"

def test_with_real_signature():
    """Test webhook mit ECHTER Stripe-Signatur"""
    print("🔐 TESTE MIT ECHTER STRIPE-SIGNATUR...")
    
    # Test webhook secret (würde normalerweise aus Environment kommen)
    webhook_secret = "whsec_test_secret_for_testing"  # Placeholder
    
    webhook_url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    # Stripe-konforme Payload
    payload = {
        "id": "evt_real_signature_test",
        "object": "event",
        "api_version": "2024-06-20",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_real_signature_test",
                "object": "checkout.session",
                "amount_total": 999,
                "currency": "eur",
                "customer": "cus_test",
                "mode": "payment",
                "payment_status": "paid",
                "status": "complete",
                "metadata": {
                    "user_id": "e747de39-1b54-4cd0-96eb-e68f155931e2",
                    "credits": "100"
                }
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {"id": "req_test", "idempotency_key": None},
        "type": "checkout.session.completed"
    }
    
    payload_string = json.dumps(payload, separators=(',', ':'))
    real_signature = generate_real_stripe_signature(payload_string, webhook_secret)
    
    headers = {
        "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        "Content-Type": "application/json",
        "Stripe-Signature": real_signature
    }
    
    print(f"🚀 POST mit echter Signatur...")
    print(f"📝 Signature: {real_signature}")
    
    try:
        response = requests.post(webhook_url, data=payload_string, headers=headers, timeout=20)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📤 Response: {response.text}")
        
        if response.status_code == 200:
            print("🎉 ERFOLG: Webhook mit echter Signatur funktioniert!")
            return True
        elif response.status_code == 400:
            if "signature" in response.text.lower():
                print("⚠️ Signatur-Validierung fehlgeschlagen - Secret stimmt nicht überein")
                print("🔧 Webhook Secret muss in Render Environment gesetzt werden")
            else:
                print("❌ Anderer Payload-Fehler")
            return False
        else:
            print(f"❓ Unerwarteter Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def test_development_bypass():
    """Test mit Development-Bypass (ohne Signatur)"""
    print("\n🧪 TESTE DEVELOPMENT-BYPASS...")
    
    # Dieser Test würde funktionieren wenn STRIPE_WEBHOOK_BYPASS_SIGNATURE=true gesetzt ist
    webhook_url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    payload = {
        "id": "evt_bypass_test",
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
        # Bewusst KEINE Stripe-Signature für Bypass-Test
    }
    
    print(f"🚀 POST ohne Signatur (Bypass-Modus erforderlich)...")
    
    try:
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=15)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📤 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Development-Bypass funktioniert!")
            return True
        elif response.status_code == 400 and "missing signature" in response.text.lower():
            print("⚠️ Bypass-Modus nicht aktiviert - Signatur erforderlich")
            return False
        else:
            print(f"❓ Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def stripe_cli_instructions():
    """Anweisungen für Stripe CLI Testing"""
    print("\n📋 STRIPE CLI TESTING (BESTE METHODE):")
    print("=" * 50)
    
    print("1. 📦 Stripe CLI installieren:")
    print("   https://stripe.com/docs/stripe-cli")
    
    print("\n2. 🔑 Login:")
    print("   stripe login")
    
    print("\n3. 🎯 Webhook forwarding:")
    print("   stripe listen --forward-to https://resume-matcher-backend-j06k.onrender.com/")
    
    print("\n4. 🧪 Test events triggern:")
    print("   stripe trigger checkout.session.completed \\")
    print("     --add checkout_session:metadata[user_id]=e747de39-1b54-4cd0-96eb-e68f155931e2 \\")
    print("     --add checkout_session:metadata[credits]=100")
    
    print("\n✅ VORTEILE:")
    print("   - Echte Stripe-Signaturen")
    print("   - Korrekte Event-Struktur")
    print("   - Live-Testing möglich")

def webhook_development_setup():
    """Setup für lokale Webhook-Entwicklung"""
    print("\n🔧 DEVELOPMENT SETUP:")
    print("=" * 30)
    
    print("1. 🌐 Environment Variables setzen:")
    print("   STRIPE_WEBHOOK_BYPASS_SIGNATURE=true  # NUR für Development!")
    print("   ENV=development")
    print("   STRIPE_WEBHOOK_SECRET=whsec_test_...")
    
    print("\n2. 🔄 Backend neu starten mit neuen Env Vars")
    
    print("\n3. 🧪 Test ohne Signatur ausführen")
    
    print("\n⚠️ WICHTIG:")
    print("   NIEMALS STRIPE_WEBHOOK_BYPASS_SIGNATURE=true in Production!")

def main():
    print("🔧 STRIPE WEBHOOK SIGNATURE FIX")
    print("=" * 50)
    
    print("❌ MEIN FEHLER KORRIGIERT:")
    print("   Stripe signiert ALLE Webhooks (Test + Live)")
    print("   Unsere fake Signaturen wurden korrekt abgelehnt!")
    
    # Test mit echter Signatur
    real_sig_works = test_with_real_signature()
    
    # Test development bypass
    bypass_works = test_development_bypass()
    
    # Anweisungen
    stripe_cli_instructions()
    webhook_development_setup()
    
    print(f"\n📊 TEST ERGEBNISSE:")
    print(f"   Echte Signatur: {'✅' if real_sig_works else '❌'}")
    print(f"   Development Bypass: {'✅' if bypass_works else '❌'}")
    
    print(f"\n🎯 EMPFOHLENE LÖSUNG:")
    if not real_sig_works and not bypass_works:
        print("1. 🔧 Webhook-Code mit Development-Bypass erweitern")
        print("2. 🧪 Stripe CLI für echte Tests verwenden")
        print("3. 📊 Environment Variable für Bypass setzen")
        print("4. 🚀 Production mit echter Signatur-Validierung")
    elif bypass_works:
        print("✅ Development-Bypass funktioniert bereits!")
        print("🧪 Für Production: Stripe CLI oder Dashboard verwenden")
    else:
        print("🎉 Webhook funktioniert mit echter Signatur!")
    
    print(f"\n💡 NÄCHSTE SCHRITTE:")
    print("1. Backend-Code mit korrekter Signatur-Handling updaten")
    print("2. Development-Bypass implementieren")  
    print("3. Stripe CLI setup für echte Tests")
    print("4. Production mit Live-Webhooks testen")

if __name__ == "__main__":
    main()
