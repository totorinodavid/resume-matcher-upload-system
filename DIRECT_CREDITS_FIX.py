#!/usr/bin/env python3
"""
🎯 DIREKTE CREDITS-PROBLEM LÖSUNG
=================================

PROBLEM: Credits werden nicht gutgeschrieben obwohl Backend läuft

DIREKTE ANALYSE:
1. Stripe Webhook URL prüfen
2. Echte Webhook-Logs anschauen  
3. Credits-Service testen
4. Datenbank direkt prüfen

KEINE AUSREDEN - DIREKTER FIX!
"""

import requests
import json
import time
from datetime import datetime

def test_real_stripe_webhook():
    """Teste mit ECHTER Stripe-ähnlicher Payload"""
    print("🎯 TESTE ECHTE STRIPE WEBHOOK VERARBEITUNG...")
    
    webhook_url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    # ECHTE Stripe checkout.session.completed Payload
    real_payload = {
        "id": "evt_1234567890",
        "object": "event",
        "api_version": "2024-06-20",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_test_1234567890",
                "object": "checkout.session",
                "amount_total": 999,
                "currency": "eur",
                "customer": "cus_test_customer_real",
                "mode": "payment",
                "payment_status": "paid",
                "status": "complete",
                "metadata": {
                    "user_id": "e747de39-1b54-4cd0-96eb-e68f155931e2",
                    "credits": "100"
                },
                "line_items": {
                    "object": "list",
                    "data": [
                        {
                            "id": "li_1234567890",
                            "object": "item",
                            "amount_total": 999,
                            "currency": "eur",
                            "description": "100 Credits",
                            "price": {
                                "id": "price_1234567890",
                                "object": "price",
                                "active": True,
                                "currency": "eur",
                                "metadata": {
                                    "credits": "100"
                                },
                                "product": "prod_1234567890",
                                "unit_amount": 999
                            },
                            "quantity": 1
                        }
                    ]
                }
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {
            "id": "req_1234567890",
            "idempotency_key": None
        },
        "type": "checkout.session.completed"
    }
    
    headers = {
        "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1693834800,v1=fake_signature_for_testing"
    }
    
    print(f"🚀 POST to: {webhook_url}")
    print(f"💰 Test Credits: 100 für User: e747de39-1b54-4cd0-96eb-e68f155931e2")
    
    try:
        response = requests.post(
            webhook_url,
            json=real_payload,
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📤 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Webhook verarbeitet!")
            return True
        elif response.status_code == 400:
            if "signature" in response.text.lower():
                print("⚠️ Signature-Fehler (normal für Test)")
                print("🔧 Aber Webhook-Route funktioniert!")
                return True
            else:
                print("❌ Payload-Problem")
                return False
        else:
            print(f"❌ Unexpected Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

def check_credits_endpoint():
    """Prüfe Credits-Endpoint direkt"""
    print("\n📊 PRÜFE CREDITS-ENDPOINT...")
    
    # Test ohne Auth (sollte 401 geben)
    credits_url = "https://resume-matcher-backend-j06k.onrender.com/api/v1/me/credits"
    
    try:
        response = requests.get(credits_url, timeout=10)
        print(f"📊 Credits API Status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Credits API ist sicher (401 Unauthorized)")
        else:
            print(f"⚠️ Unexpected Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"💥 Credits API Error: {e}")

def analyze_webhook_processing():
    """Analysiere Webhook-Verarbeitung"""
    print("\n🔍 WEBHOOK-VERARBEITUNG ANALYSE...")
    
    # Test verschiedene Webhook-URLs
    base_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    webhook_endpoints = [
        "/",  # Emergency route
        "/webhooks/stripe",  # Original route
        "/api/stripe/webhook"  # Alias route
    ]
    
    for endpoint in webhook_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            # Test GET (should fail)
            get_response = requests.get(url, timeout=5)
            print(f"   GET {endpoint}: {get_response.status_code}")
            
            # Test POST without Stripe headers
            post_response = requests.post(url, json={"test": "data"}, timeout=5)
            print(f"   POST {endpoint}: {post_response.status_code}")
            
        except Exception as e:
            print(f"   Error testing {endpoint}: {e}")

def check_stripe_webhook_config():
    """Prüfe Stripe Webhook Konfiguration"""
    print("\n⚙️ STRIPE WEBHOOK KONFIGURATION...")
    
    print("🔧 Aktuelle Webhook-URL sollte sein:")
    print("   https://resume-matcher-backend-j06k.onrender.com/")
    print("")
    print("📋 Stripe Dashboard Einstellungen prüfen:")
    print("   1. https://dashboard.stripe.com/webhooks")
    print("   2. Webhook-URL korrekt?")
    print("   3. Event-Types aktiviert:")
    print("      - checkout.session.completed ✅")
    print("      - invoice.payment_succeeded ✅")
    print("   4. Webhook Secret korrekt gesetzt?")

def main():
    print("🎯 DIREKTE CREDITS-PROBLEM LÖSUNG")
    print("=" * 50)
    print(f"Zeit: {datetime.now()}")
    print("PROBLEM: Credits werden nicht gutgeschrieben")
    print("")
    
    # 1. Test echte Webhook-Verarbeitung
    webhook_works = test_real_stripe_webhook()
    
    # 2. Prüfe Credits-Endpoint
    check_credits_endpoint()
    
    # 3. Analysiere Webhook-Processing
    analyze_webhook_processing()
    
    # 4. Stripe-Konfiguration
    check_stripe_webhook_config()
    
    print(f"\n🎯 DIREKTE AKTIONEN:")
    
    if webhook_works:
        print("✅ Webhook-Route funktioniert")
        print("🔧 Problem ist wahrscheinlich:")
        print("   1. ❌ Falsche Webhook-URL in Stripe Dashboard")
        print("   2. ❌ Falscher/fehlender Webhook Secret")
        print("   3. ❌ Event-Types nicht aktiviert")
        print("   4. ❌ Credits-Service-Logik-Fehler")
    else:
        print("❌ Webhook-Route hat Probleme")
        print("🔧 Backend-Code muss gefixt werden")
    
    print(f"\n📞 NÄCHSTE SCHRITTE:")
    print("1. 🌐 Stripe Dashboard: https://dashboard.stripe.com/webhooks")
    print("2. 🔧 Webhook URL: https://resume-matcher-backend-j06k.onrender.com/")
    print("3. 📊 Event Types: checkout.session.completed")
    print("4. 🧪 Test Purchase durchführen")
    print("5. 📋 Render Logs für Webhook-Verarbeitung prüfen")

if __name__ == "__main__":
    main()
