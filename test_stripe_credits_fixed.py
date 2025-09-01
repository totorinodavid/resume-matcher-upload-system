#!/usr/bin/env python3
"""
🧪 AUTOMATISCHER STRIPE CREDITS TEST
===================================
Testet die komplette Credits-Pipeline nach den Fixes
"""

import requests
import json
import time
from datetime import datetime

def test_complete_credits_flow():
    """Testet den kompletten Credits-Flow"""
    
    print("🧪 AUTOMATISCHER STRIPE CREDITS TEST")
    print("="*50)
    
    # Test 1: Environment Check
    print("\n1. Environment Check...")
    response = requests.get("https://resume-matcher-backend-j06k.onrender.com/health")
    if response.status_code == 200:
        print("✅ Backend erreichbar")
    else:
        print("❌ Backend nicht erreichbar")
    
    # Test 2: Webhook Debug
    print("\n2. Webhook Debug Test...")
    test_webhook = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": None,
                "metadata": {
                    "user_id": "test_user_123",
                    "credits": "100",
                    "price_id": "price_test"
                }
            }
        }
    }
    
    try:
        response = requests.post(
            "https://resume-matcher-backend-j06k.onrender.com/webhooks/stripe/debug",
            json=test_webhook,
            headers={"Stripe-Signature": "t=1693906800,v1=test_signature"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook Debug Response: {result}")
            
            if result.get("user_id_resolved"):
                print("✅ User-ID Resolution funktioniert!")
            else:
                print("❌ User-ID Resolution fehlgeschlagen")
        else:
            print(f"⚠️ Webhook Debug Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Webhook Debug Error: {e}")
    
    # Test 3: Authentication Check
    print("\n3. Authentication Check...")
    response = requests.post(
        "https://gojob.ing/api/stripe/checkout",
        json={"price_id": "price_test"},
        timeout=10
    )
    
    if response.status_code == 401:
        print("✅ Checkout Authentication funktioniert")
    else:
        print(f"⚠️ Checkout Authentication Status: {response.status_code}")
    
    print("\n🎯 TEST ABGESCHLOSSEN")
    print("Führen Sie nun einen echten Test-Kauf durch!")

if __name__ == "__main__":
    test_complete_credits_flow()
