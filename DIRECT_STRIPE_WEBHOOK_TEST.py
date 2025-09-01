#!/usr/bin/env python3
"""
🚀 DIRECT STRIPE WEBHOOK TEST
=============================

Simple test script that directly tests the Ultimate Stripe Webhook handler
without health checks that might fail due to missing endpoints.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"
TEST_USER_ID = "e747de39-1b54-4cd0-96eb-e68f155931e2"


def create_test_webhook_payload(user_id: str, credits: int = 100) -> Dict[str, Any]:
    """Create a test webhook payload that mimics Stripe's checkout.session.completed event"""
    return {
        "id": f"evt_test_{int(time.time())}",
        "object": "event",
        "api_version": "2023-10-16",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": f"cs_test_{int(time.time())}",
                "object": "checkout.session",
                "customer": f"cus_test_{int(time.time())}",
                "payment_status": "paid",
                "metadata": {
                    "user_id": user_id,
                    "credits": str(credits)
                },
                "mode": "payment",
                "status": "complete"
            }
        },
        "livemode": False,
        "pending_webhooks": 0,
        "request": {
            "id": None,
            "idempotency_key": None
        },
        "type": "checkout.session.completed"
    }


async def test_ultimate_webhook():
    """Test the ultimate webhook implementation directly"""
    logger.info("🔧 Testing Ultimate Stripe Webhook Implementation")
    logger.info(f"   Backend URL: {BACKEND_URL}")
    logger.info(f"   Test User ID: {TEST_USER_ID}")
    logger.info("=" * 60)
    
    # Create test payload
    payload = create_test_webhook_payload(TEST_USER_ID, credits=100)
    
    headers = {
        "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1234567890,v1=test_signature_for_ultimate_fix"
    }
    
    logger.info("📤 Sending webhook to root endpoint (Ultimate Fix)...")
    logger.info(f"   Event Type: {payload['type']}")
    logger.info(f"   User ID: {payload['data']['object']['metadata']['user_id']}")
    logger.info(f"   Credits: {payload['data']['object']['metadata']['credits']}")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/",
                json=payload,
                headers=headers
            )
            
            logger.info(f"📥 Response Status: {response.status_code}")
            logger.info(f"📥 Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                logger.info(f"📥 Response Body:")
                logger.info(json.dumps(response_data, indent=2))
                
                # Analyze response
                if response.status_code == 200:
                    if response_data.get("ok"):
                        if "credits_added" in response_data:
                            logger.info("🎉 SUCCESS: Ultimate Webhook Fix is working!")
                            logger.info(f"   ✅ User ID: {response_data.get('user_id')}")
                            logger.info(f"   ✅ Credits Added: {response_data.get('credits_added')}")
                            logger.info(f"   ✅ Event ID: {response_data.get('event_id')}")
                            return True
                        elif "error" in response_data:
                            error = response_data["error"]
                            logger.error(f"❌ WEBHOOK ERROR: {error}")
                            
                            if error == "no_user_mapping":
                                logger.error("   Root cause: User ID resolution failed")
                                logger.error("   Check: Metadata is being passed correctly")
                            elif error == "no_credits": 
                                logger.error("   Root cause: Credits not found in metadata")
                                logger.error("   Check: Credits field in session metadata")
                            else:
                                logger.error(f"   Unexpected error: {error}")
                            return False
                        elif "skipped" in response_data:
                            skipped = response_data["skipped"]
                            logger.warning(f"⚠️ WEBHOOK SKIPPED: {skipped}")
                            return False
                        else:
                            logger.warning("⚠️ Webhook acknowledged but no specific result")
                            return False
                    else:
                        logger.error("❌ WEBHOOK FAILED: Response not ok")
                        return False
                else:
                    logger.error(f"❌ HTTP ERROR: {response.status_code}")
                    if response.status_code == 400:
                        logger.error("   Likely cause: Signature verification failed")
                    elif response.status_code == 404:
                        logger.error("   Likely cause: Endpoint not found or not a Stripe webhook")
                    elif response.status_code == 503:
                        logger.error("   Likely cause: Webhook not configured (missing secret)")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Failed to parse response JSON: {e}")
                logger.error(f"   Raw response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return False


async def test_multiple_scenarios():
    """Test multiple webhook scenarios"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 Testing Multiple Webhook Scenarios")
    logger.info("=" * 60)
    
    scenarios = [
        {
            "name": "Standard Payment (100 credits)",
            "credits": 100,
            "expected_success": True
        },
        {
            "name": "Large Payment (500 credits)",
            "credits": 500,
            "expected_success": True
        },
        {
            "name": "Small Payment (10 credits)",
            "credits": 10,
            "expected_success": True
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        logger.info(f"\n📋 Test {i}/{len(scenarios)}: {scenario['name']}")
        
        # Create payload for this scenario
        payload = create_test_webhook_payload(TEST_USER_ID, credits=scenario["credits"])
        
        headers = {
            "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
            "Content-Type": "application/json", 
            "Stripe-Signature": f"t={int(time.time())},v1=scenario_{i}_signature"
        }
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(
                    f"{BACKEND_URL}/",
                    json=payload,
                    headers=headers
                )
                
                response_data = response.json() if response.status_code == 200 else {}
                success = (
                    response.status_code == 200 and
                    response_data.get("ok") and
                    "credits_added" in response_data and
                    response_data["credits_added"] == scenario["credits"]
                )
                
                if success:
                    logger.info(f"   ✅ SUCCESS: {response_data['credits_added']} credits added")
                    results.append(True)
                else:
                    logger.error(f"   ❌ FAILED: {response_data.get('error', 'Unknown error')}")
                    results.append(False)
                
                # Small delay between tests
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"   ❌ Test failed with exception: {e}")
                results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    logger.info(f"\n📊 Scenario Results: {success_count}/{total_count} passed")
    
    return success_count == total_count


async def main():
    """Run the direct webhook test"""
    logger.info("🚀 Direct Ultimate Stripe Webhook Test")
    logger.info("=" * 60)
    
    # Test 1: Basic webhook functionality
    basic_success = await test_ultimate_webhook()
    
    if basic_success:
        # Test 2: Multiple scenarios
        scenarios_success = await test_multiple_scenarios()
    else:
        scenarios_success = False
    
    # Final results
    logger.info("\n" + "=" * 60)
    logger.info("🏁 FINAL TEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"   Basic Webhook Test: {'✅ PASS' if basic_success else '❌ FAIL'}")
    logger.info(f"   Multiple Scenarios: {'✅ PASS' if scenarios_success else '❌ FAIL'}")
    
    if basic_success and scenarios_success:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("   The Ultimate Stripe Webhook Fix is working perfectly!")
        logger.info("   ✅ Webhooks are being received and processed")
        logger.info("   ✅ User resolution is working correctly") 
        logger.info("   ✅ Credits are being added to user accounts")
        logger.info("   ✅ Multiple payment amounts work correctly")
    elif basic_success:
        logger.info("\n⚠️ BASIC TEST PASSED, but scenarios need work")
    else:
        logger.error("\n❌ BASIC TEST FAILED")
        logger.error("   The Ultimate Webhook Fix needs debugging")
        logger.error("   Check server logs for detailed error information")
    
    return basic_success and scenarios_success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
