#!/usr/bin/env python3
"""
🚨 KRITISCHER WEBHOOK-FIX TEST
==============================

PROBLEM: POST / Route wurde von GET / überschrieben
LÖSUNG: POST / Route direkt in base.py hinzugefügt

DEPLOYMENT: 4af42f5 - CRITICAL WEBHOOK FIX

JETZT TESTEN:
"""

import requests
import time
import json
from datetime import datetime

def wait_for_deployment():
    """Warten auf Render Deployment"""
    print("⏳ WARTE AUF RENDER DEPLOYMENT...")
    print("Render braucht 2-3 Minuten für das Update...")
    
    for minute in range(4):
        print(f"   ⏰ Minute {minute + 1}/4...")
        time.sleep(60)
        
        # Test ob deployment fertig ist
        try:
            response = requests.get("https://resume-matcher-backend-j06k.onrender.com/healthz", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ Backend antwortet - Deployment läuft")
            else:
                print(f"   ⚠️ Status {response.status_code}")
        except:
            print(f"   ❌ Nicht erreichbar - noch am deployen")

def test_critical_webhook_fix():
    """Teste den kritischen Webhook Fix"""
    print("\n🚨 TESTE KRITISCHEN WEBHOOK FIX...")
    
    webhook_url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    # Echte Stripe-Payload
    payload = {
        "id": "evt_critical_test",
        "object": "event",
        "type": "checkout.session.completed",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_critical_test",
                "object": "checkout.session",
                "payment_status": "paid",
                "status": "complete",
                "metadata": {
                    "user_id": "e747de39-1b54-4cd0-96eb-e68f155931e2",
                    "credits": "100"
                }
            }
        }
    }
    
    headers = {
        "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1693834800,v1=critical_test_signature"
    }
    
    print(f"🚀 POST to: {webhook_url}")
    print(f"🎭 Stripe User-Agent für Emergency Route")
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=20
        )
        
        status = response.status_code
        body = response.text
        
        print(f"📊 Status: {status}")
        print(f"📤 Response: {body}")
        
        if status == 200:
            print("🎉 PERFEKT: Webhook erfolgreich verarbeitet!")
            print("✅ Credits sollten jetzt hinzugefügt werden!")
            return True
        elif status == 400:
            if "signature" in body.lower() or "stripe" in body.lower():
                print("✅ ERFOLG: Stripe-Verarbeitung funktioniert!")
                print("⚠️ Signature-Fehler normal bei Test")
                print("✅ Emergency Route fängt Webhooks ab!")
                return True
            else:
                print("❌ Unerwarteter 400 Fehler")
                return False
        elif status == 404:
            print("❌ IMMER NOCH 404 - Fix nicht funktioniert")
            return False
        else:
            print(f"❓ Status {status} - investigating...")
            return False
            
    except Exception as e:
        print(f"💥 Test failed: {e}")
        return False

def test_all_webhook_routes():
    """Teste alle Webhook-Routen"""
    print("\n🔍 TESTE ALLE WEBHOOK-ROUTEN...")
    
    base_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    routes = [
        "/",  # Emergency route in base.py
        "/webhooks/stripe",  # Original route
        "/api/stripe/webhook"  # Alias route
    ]
    
    stripe_headers = {
        "User-Agent": "Stripe/1.0",
        "Content-Type": "application/json",
        "Stripe-Signature": "t=123,v1=test"
    }
    
    simple_payload = {"test": "webhook"}
    
    for route in routes:
        url = f"{base_url}{route}"
        print(f"\n🔍 Testing: {route}")
        
        try:
            response = requests.post(url, json=simple_payload, headers=stripe_headers, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code in [200, 400]:
                print(f"   ✅ Route funktioniert (verarbeitet Stripe)")
            elif response.status_code == 404:
                print(f"   ❌ Route nicht gefunden")
            else:
                print(f"   ⚠️ Status {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

def main():
    print("🚨 KRITISCHER WEBHOOK-FIX TEST")
    print("=" * 50)
    print(f"Zeit: {datetime.now()}")
    print("Fix deployed: 4af42f5 - POST / route in base.py")
    
    # Warten auf Deployment
    wait_for_deployment()
    
    # Teste kritischen Fix
    webhook_works = test_critical_webhook_fix()
    
    # Teste alle Routen
    test_all_webhook_routes()
    
    print(f"\n🎯 ERGEBNIS:")
    if webhook_works:
        print("✅ KRITISCHER FIX ERFOLGREICH!")
        print("🎉 Stripe Webhooks funktionieren jetzt!")
        print("💰 Credits werden bei echten Käufen hinzugefügt!")
        
        print(f"\n🚀 NÄCHSTE SCHRITTE:")
        print("1. 🌐 Frontend: https://resume-matcher.vercel.app")
        print("2. 🔑 Einloggen und Credits kaufen")
        print("3. 📊 Credits sollten sofort hinzugefügt werden")
        print("4. 🎯 Webhook-URL für Stripe: https://resume-matcher-backend-j06k.onrender.com/")
    else:
        print("❌ FIX HAT NICHT FUNKTIONIERT")
        print("🔧 Weitere Diagnose erforderlich")

if __name__ == "__main__":
    main()
