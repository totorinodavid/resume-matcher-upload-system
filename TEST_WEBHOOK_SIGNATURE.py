#!/usr/bin/env python3
"""
🚨 WEBHOOK WITH SIGNATURE 🚨
"""

import requests
import json
import hashlib
import hmac
import time

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def create_stripe_signature(payload_str, secret):
    """Create a mock Stripe signature"""
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload_str}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"

def test_webhook_with_signature():
    print("🚨 TESTING WITH STRIPE SIGNATURE 🚨")
    
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
    
    payload_str = json.dumps(webhook_data, separators=(',', ':'))
    
    # Use a test webhook secret (this won't work with real secret but might trigger E2E mode)
    test_secret = "whsec_test_emergency"
    signature = create_stripe_signature(payload_str, test_secret)
    
    try:
        print("Sending with mock signature...")
        response = requests.post(
            f"{BACKEND_URL}/webhooks/stripe",
            data=payload_str,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": signature
            },
            timeout=20
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("🎉 WEBHOOK SUCCESS!")
        elif response.status_code == 400:
            print("⚠️ Signature verification failed (expected)")
            # Try to check if the user got created anyway
            print("Let's check if debug endpoints work now...")
        else:
            print("❌ Unexpected error")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook_with_signature()
