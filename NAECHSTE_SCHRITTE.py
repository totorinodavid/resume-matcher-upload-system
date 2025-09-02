#!/usr/bin/env python3
"""
🚨 NÄCHSTE SCHRITTE - SOFORTIGE CREDIT-ZUWEISUNG 🚨

1. Direkte Admin-Endpoint Erstellung für Credit-Transfer
2. Sofortige Ausführung ohne Warten auf Deployment
"""

import requests
import json
import time

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def naechste_schritte():
    print("🚨 NÄCHSTE SCHRITTE - CREDIT-ZUWEISUNG 🚨")
    print("="*50)
    
    # SCHRITT 1: Test aktueller Status
    print("SCHRITT 1: Teste aktuellen Backend-Status...")
    try:
        r = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        print(f"✅ Backend erreichbar: HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ Backend nicht erreichbar: {e}")
        return
    
    # SCHRITT 2: Test E2E Webhook
    print("\nSCHRITT 2: Teste E2E Webhook...")
    webhook_data = {
        "id": "evt_final_davis_t",
        "type": "checkout.session.completed", 
        "data": {
            "object": {
                "id": "cs_final_davis_t",
                "customer": "cus_davis_t_final",
                "metadata": {
                    "user_id": "197acb67-0d0a-467f-8b63-b2886c7fff6e",
                    "credits": "50"
                }
            }
        }
    }
    
    try:
        r = requests.post(
            f"{BACKEND_URL}/webhooks/stripe",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"Webhook Status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            print("🎉 E2E WEBHOOK ERFOLGREICH!")
            result = json.loads(r.text)
            if result.get("ok"):
                print("✅ CREDITS WURDEN ZUGEWIESEN!")
            else:
                print("⚠️ Webhook OK aber Credits unklar")
        elif r.status_code == 400:
            print("⏳ E2E mode noch nicht aktiv")
        else:
            print("❌ Webhook Fehler")
            
    except Exception as e:
        print(f"❌ Webhook Error: {e}")
    
    # SCHRITT 3: Test Debug Endpoints
    print("\nSCHRITT 3: Teste Debug Endpoints...")
    try:
        r = requests.get(f"{BACKEND_URL}/admin/debug/all-users", timeout=10)
        if r.status_code == 200:
            users = r.json()
            print(f"✅ Debug Endpoints aktiv - {len(users.get('users', []))} Users gefunden")
            
            # Suche davis t
            for user in users.get('users', []):
                if 'davis' in str(user).lower() or '197acb67' in str(user):
                    print(f"🎯 Davis T gefunden: {user}")
        else:
            print(f"⏳ Debug Endpoints nicht bereit: HTTP {r.status_code}")
    except Exception as e:
        print(f"⏳ Debug Endpoints nicht erreichbar: {e}")
    
    print("\n" + "="*50)
    print("🎯 NÄCHSTE AKTIONEN:")
    print("1. Warten auf E2E_TEST_MODE Deployment")
    print("2. Webhook automatisch ausführen")  
    print("3. Credits über Debug Endpoints verifizieren")
    print("4. Falls nötig: Manuelle Credit-Zuweisung")
    print("="*50)

if __name__ == "__main__":
    naechste_schritte()
