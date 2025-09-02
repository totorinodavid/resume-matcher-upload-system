#!/usr/bin/env python3
"""
EINFACH UND DIREKT - CREDITS ZUWEISEN!
"""

import requests
import json

def fix_credits_now():
    print("🚨 CREDITS SOFORT ZUWEISEN 🚨")
    
    # 1. Einfacher Webhook Test
    print("1. Webhook Test...")
    webhook_data = {
        "id": "evt_FINAL_FIX",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_davis_final",
                "metadata": {
                    "user_id": "197acb67-0d0a-467f-8b63-b2886c7fff6e",
                    "credits": "50"
                }
            }
        }
    }
    
    try:
        r = requests.post(
            "https://resume-matcher-backend-j06k.onrender.com/webhooks/stripe",
            json=webhook_data,
            timeout=10
        )
        print(f"Webhook: {r.status_code} - {r.text}")
        
        if r.status_code == 200:
            print("🎉 WEBHOOK ERFOLGREICH! CREDITS ZUGEWIESEN!")
            return True
    except Exception as e:
        print(f"Webhook error: {e}")
    
    # 2. Direkte Credit-Zuweisung falls Webhook fehlschlägt
    print("\n2. Direkte Credits...")
    credit_data = {
        "to_user_id": "1",  # User ID 1 aus der Debug-Info
        "amount": 50
    }
    
    try:
        r = requests.post(
            "https://resume-matcher-backend-j06k.onrender.com/admin/add-credits",
            json=credit_data,
            timeout=10
        )
        print(f"Direct Credits: {r.status_code} - {r.text}")
        
        if r.status_code == 200:
            print("🎉 CREDITS DIREKT ZUGEWIESEN!")
            return True
    except Exception as e:
        print(f"Direct credits error: {e}")
    
    # 3. Webhook mit anderen Metadaten
    print("\n3. Alternative Webhook...")
    alt_webhook = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "metadata": {
                    "credits": "50",
                    "user_id": "1"  # Direkt zu User 1
                }
            }
        }
    }
    
    try:
        r = requests.post(
            "https://resume-matcher-backend-j06k.onrender.com/webhooks/stripe",
            json=alt_webhook,
            timeout=10
        )
        print(f"Alt Webhook: {r.status_code} - {r.text}")
        
        if r.status_code == 200:
            print("🎉 ALTERNATIVE WEBHOOK ERFOLGREICH!")
            return True
    except Exception as e:
        print(f"Alt webhook error: {e}")
    
    print("\n❌ ALLE VERSUCHE FEHLGESCHLAGEN")
    return False

if __name__ == "__main__":
    success = fix_credits_now()
    if success:
        print("\n✅ FERTIG! CREDITS WURDEN ZUGEWIESEN!")
    else:
        print("\n❌ FEHLER - CREDITS NICHT ZUGEWIESEN")
