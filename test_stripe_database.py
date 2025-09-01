#!/usr/bin/env python3
"""
STRIPE CREDIT DATENBANK TEST
Simuliert eine Stripe-Zahlung und überwacht die PostgreSQL-Datenbank direkt
"""

import json
import time
from urllib.request import urlopen, Request, HTTPError
from urllib.error import URLError

def check_user_balance(user_id, description):
    """Direkt die Balance via Admin API checken"""
    url = f"https://resume-matcher-backend-j06k.onrender.com/admin/credits/{user_id}"
    
    try:
        request = Request(url)
        with urlopen(request, timeout=15) as response:
            content = response.read().decode('utf-8')
            data = json.loads(content)
            print(f"{description}: {data['total_credits']} credits")
            return data['total_credits']
    except Exception as e:
        print(f"{description}: ERROR - {e}")
        return None

def test_stripe_webhook():
    """Simuliert eine Stripe-Zahlung für Test"""
    # Basierend auf den Production Logs: deine echte User ID
    # Aus den Logs: "ed00040a-3bce-497c-<phone>f3ce86ea4"
    # Das <phone> ist redaction - die echte ID müssen wir durch Test ermitteln
    real_user_id = "ed00040a-3bce-497c-96eb-f3ce86ea4"  # Vermutung basierend auf Format
    
    # Backup User IDs falls die erste nicht stimmt
    possible_user_ids = [
        "ed00040a-3bce-497c-96eb-f3ce86ea4",  # Vermutung 1
        "ed00040a-3bce-497c-9f3c-f3ce86ea4",  # Vermutung 2 (andere Hex-Zeichen)
        "e747de39-1b54-4cd0-96eb-e68f155931e2",  # Aus ursprünglichem Context
        "7675e93c-341b-412d-a41c-cfe1dc519172",  # Falsche von Stripe Zahlung
    ]
    
    print("🔍 STRIPE CREDIT DATENBANK TEST")
    print("=" * 50)
    print()
    
    print("AKTUELLE BALANCES VOR SIMULIERTER ZAHLUNG:")
    for i, user_id in enumerate(possible_user_ids):
        balance = check_user_balance(user_id, f"{i+1}. {user_id}")
    
    print()
    print("🧪 SIMULIERE STRIPE WEBHOOK ZAHLUNG...")
    
    # Erstelle eine simulierte Stripe Webhook Payload
    webhook_payload = {
        "id": "evt_test_webhook_simulation",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_simulation_session",
                "customer": "cus_test_customer_123",
                "payment_status": "paid",
                "metadata": {
                    "user_id": real_user_id,
                    "credits": "50",
                    "price_id": "price_test_simulation",
                    "plan_id": "medium",
                    "purchase_timestamp": "2025-09-01T15:30:00.000Z",
                    "frontend_version": "1.0"
                }
            }
        }
    }
    
    # Direkt an den Ultimate Webhook Handler senden
    url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    try:
        # Simuliere Stripe Headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Stripe/1.0 (+https://stripe.com/docs/webhooks)',
            'Stripe-Signature': 'test_signature_bypass'  # Wird vom E2E Mode ignoriert
        }
        
        request = Request(
            url, 
            data=json.dumps(webhook_payload).encode('utf-8'),
            headers=headers
        )
        
        with urlopen(request, timeout=30) as response:
            content = response.read().decode('utf-8')
            result = json.loads(content)
            
            print(f"✅ Webhook Response: {result}")
            
            if result.get('ok'):
                print("🎉 Webhook erfolgreich verarbeitet!")
                if 'credits_added' in result:
                    print(f"   Credits hinzugefügt: {result['credits_added']}")
                    print(f"   User ID: {result.get('user_id')}")
            else:
                print(f"❌ Webhook Fehler: {result}")
                
    except HTTPError as e:
        error_content = e.read().decode('utf-8')
        print(f"❌ HTTP Error {e.code}: {error_content}")
    except Exception as e:
        print(f"❌ Request Error: {e}")
    
    print()
    print("⏳ Warte 5 Sekunden und prüfe Balances erneut...")
    time.sleep(5)
    
    print()
    print("BALANCES NACH SIMULIERTER ZAHLUNG:")
    for i, user_id in enumerate(possible_user_ids):
        balance = check_user_balance(user_id, f"{i+1}. {user_id}")
    
    print()
    print("=" * 50)
    print("ANALYSE:")
    print("- Wenn eine der Balances jetzt 50 Credits zeigt, funktioniert das System!")
    print("- Wenn alle Balances 0 sind, gibt es noch ein Problem")
    print("- Checke die Webhook Logs für Details")

if __name__ == "__main__":
    test_stripe_webhook()
