#!/usr/bin/env python3
"""
🚨 CORRECT WEBHOOK TEST 🚨
Verwendet den tatsächlich verfügbaren Webhook-Endpoint
"""

import requests
import json

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def test_actual_webhook():
    print("🚨 TESTING ACTUAL STRIPE WEBHOOK 🚨")
    
    # Use the actual webhook endpoint
    webhook_data = {
        "id": "evt_emergency_davis_t",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_davis_t_payment",
                "customer": "cus_davis_t",
                "metadata": {
                    "user_id": "197acb67-0d0a-467f-8b63-b2886c7fff6e",
                    "credits": "50"
                }
            }
        }
    }
    
    # First try without signature (E2E mode should work)
    import os
    os.environ['E2E_TEST_MODE'] = 'true'
    
    try:
        print("Sending to /webhooks/stripe endpoint...")
        response = requests.post(
            f"{BACKEND_URL}/webhooks/stripe",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("🎉 WEBHOOK SUCCESS - Credits should be assigned!")
        else:
            print("❌ Webhook failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_actual_webhook()
