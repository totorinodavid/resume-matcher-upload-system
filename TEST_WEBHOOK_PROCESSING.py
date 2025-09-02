#!/usr/bin/env python3
"""
Test webhook processing after migration fix
Send a test Stripe event to verify credits system works
"""

import asyncio
import aiohttp
import json
import hashlib
import hmac
import time

async def test_webhook_processing():
    print("🧪 TESTING WEBHOOK PROCESSING")
    print("==============================")
    
    # Backend URL
    base_url = "https://resume-matcher-backend-service.onrender.com"
    webhook_url = f"{base_url}/api/webhooks/stripe"
    
    # Test payload - simulated payment.intent.succeeded event
    test_payload = {
        "id": "evt_test_webhook_processing",
        "object": "event",
        "api_version": "2020-08-27",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "pi_test_webhook_processing",
                "object": "payment_intent",
                "amount": 999,  # $9.99
                "currency": "usd",
                "status": "succeeded",
                "metadata": {
                    "user_id": "test_user_webhook_processing",
                    "credits": "10"
                }
            }
        },
        "type": "payment_intent.succeeded",
        "pending_webhooks": 1,
        "request": {
            "id": None,
            "idempotency_key": None
        }
    }
    
    payload_json = json.dumps(test_payload, separators=(',', ':'))
    
    # Create test signature (using a test secret)
    test_secret = "whsec_test_123"
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload_json}"
    signature = hmac.new(
        test_secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'Stripe-Signature': f't={timestamp},v1={signature}'
    }
    
    print(f"🚀 Sending test webhook to: {webhook_url}")
    print(f"📦 Payload type: {test_payload['type']}")
    print(f"💰 Credits: {test_payload['data']['object']['metadata']['credits']}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, data=payload_json, headers=headers) as response:
                status = response.status
                text = await response.text()
                
                print(f"📡 Response Status: {status}")
                print(f"📄 Response Body: {text}")
                
                if status == 200:
                    print("✅ Webhook processed successfully!")
                    return True
                else:
                    print(f"❌ Webhook failed with status {status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False

async def check_backend_health():
    print("\n🏥 CHECKING BACKEND HEALTH")
    print("===========================")
    
    base_url = "https://resume-matcher-backend-service.onrender.com"
    health_url = f"{base_url}/healthz"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(health_url) as response:
                status = response.status
                text = await response.text()
                
                print(f"📡 Health Status: {status}")
                print(f"📄 Health Response: {text}")
                
                return status == 200
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def main():
    print("🎯 WEBHOOK PROCESSING TEST")
    print("==========================")
    
    # First check if backend is healthy
    if not await check_backend_health():
        print("❌ Backend not healthy, skipping webhook test")
        return
    
    # Test webhook processing
    success = await test_webhook_processing()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Credits system is working correctly")
    else:
        print("\n❌ WEBHOOK TEST FAILED")
        print("🔧 Credits system needs further debugging")

if __name__ == "__main__":
    asyncio.run(main())
