#!/usr/bin/env python3
"""
🚨 MINIMAL STRIPE TEST 🚨
Testet direkt ob Credits verarbeitet wurden
"""

import requests
import json

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def test_webhook():
    print("🚨 TESTING STRIPE WEBHOOK 🚨")
    
    # Test webhook with davis t's payment
    webhook_data = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test_davis_t_payment",
                "amount": 500,  # $5.00 for 50 credits
                "metadata": {
                    "user_id": "197acb67-0d0a-467f-8b63-b2886c7fff6e",
                    "credits": "50"
                }
            }
        }
    }
    
    try:
        print("Sending webhook to emergency endpoint...")
        response = requests.post(
            f"{BACKEND_URL}/webhooks/stripe/emergency",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
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
    test_webhook()
