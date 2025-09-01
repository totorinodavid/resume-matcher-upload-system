#!/usr/bin/env python3
"""
🧪 ULTIMATE STRIPE WEBHOOK TEST
===============================

Comprehensive testing script for the ultimate Stripe webhook fix.
Tests the new webhook handler with enhanced user resolution and credit assignment.

Run this after implementing the webhook fix to validate the solution.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict, Any, Optional

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


async def test_webhook_endpoint():
    """Test the ultimate webhook endpoint"""
    logger.info("🧪 Starting Ultimate Stripe Webhook Test")
    logger.info(f"   Backend URL: {BACKEND_URL}")
    logger.info(f"   Test User ID: {TEST_USER_ID}")
    
    # Create test payload
    payload = create_test_webhook_payload(TEST_USER_ID, credits=100)
    
    headers = {
        "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1234567890,v1=test_signature_would_be_here"
    }
    
    logger.info("📤 Sending test webhook to root endpoint...")
    logger.info(f"   Payload: {json.dumps(payload, indent=2)}")
    
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
                logger.info(f"📥 Response Body: {json.dumps(response_data, indent=2)}")
                
                # Analyze response
                if response.status_code == 200:
                    if response_data.get("ok"):
                        if "credits_added" in response_data:
                            logger.info("✅ SUCCESS: Credits were added!")
                            logger.info(f"   User ID: {response_data.get('user_id')}")
                            logger.info(f"   Credits Added: {response_data.get('credits_added')}")
                            logger.info(f"   Event ID: {response_data.get('event_id')}")
                            return True
                        elif "error" in response_data:
                            logger.error(f"❌ WEBHOOK ERROR: {response_data['error']}")
                            return False
                        else:
                            logger.warning("⚠️ Webhook acknowledged but no credits info")
                            return False
                    else:
                        logger.error("❌ WEBHOOK FAILED: Response not ok")
                        return False
                else:
                    logger.error(f"❌ HTTP ERROR: {response.status_code}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Failed to parse response JSON: {e}")
                logger.error(f"   Raw response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return False


async def test_user_resolution_scenarios():
    """Test different user resolution scenarios"""
    logger.info("🧪 Testing User Resolution Scenarios")
    
    scenarios = [
        {
            "name": "Valid User ID in Metadata",
            "payload": create_test_webhook_payload(TEST_USER_ID, 50),
            "expected_success": True
        },
        {
            "name": "Empty Metadata",
            "payload": {
                **create_test_webhook_payload(TEST_USER_ID, 50),
                "data": {
                    "object": {
                        **create_test_webhook_payload(TEST_USER_ID, 50)["data"]["object"],
                        "metadata": {}
                    }
                }
            },
            "expected_success": False
        },
        {
            "name": "No Credits in Metadata", 
            "payload": {
                **create_test_webhook_payload(TEST_USER_ID, 0),
                "data": {
                    "object": {
                        **create_test_webhook_payload(TEST_USER_ID, 0)["data"]["object"],
                        "metadata": {
                            "user_id": TEST_USER_ID
                            # No credits field
                        }
                    }
                }
            },
            "expected_success": False
        }
    ]
    
    headers = {
        "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1234567890,v1=test_signature_would_be_here"
    }
    
    results = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for scenario in scenarios:
            logger.info(f"\n📋 Testing: {scenario['name']}")
            
            try:
                response = await client.post(
                    f"{BACKEND_URL}/",
                    json=scenario["payload"],
                    headers=headers
                )
                
                response_data = response.json() if response.status_code == 200 else {}
                success = (
                    response.status_code == 200 and
                    response_data.get("ok") and
                    "credits_added" in response_data
                )
                
                logger.info(f"   Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
                logger.info(f"   Expected: {'SUCCESS' if scenario['expected_success'] else 'FAILURE'}")
                
                if success == scenario["expected_success"]:
                    logger.info(f"   ✅ Scenario behaved as expected")
                    results.append(True)
                else:
                    logger.error(f"   ❌ Scenario did NOT behave as expected")
                    results.append(False)
                    
                # Small delay between tests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"   ❌ Test failed with exception: {e}")
                results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    logger.info(f"\n📊 Scenario Testing Results: {success_count}/{total_count} passed")
    
    return success_count == total_count


async def test_health_check():
    """Test if the backend is accessible"""
    logger.info("🏥 Testing Backend Health")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Try the correct health endpoint
            response = await client.get(f"{BACKEND_URL}/ping")
            if response.status_code == 200:
                logger.info("✅ Backend is healthy")
                return True
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return False


async def main():
    """Run all tests"""
    logger.info("🚀 Starting Ultimate Stripe Webhook Test Suite")
    logger.info("=" * 60)
    
    # Test 1: Health Check
    health_ok = await test_health_check()
    if not health_ok:
        logger.error("❌ Backend is not accessible. Stopping tests.")
        return False
    
    # Test 2: Basic Webhook Test
    logger.info("\n" + "=" * 60)
    webhook_ok = await test_webhook_endpoint()
    
    # Test 3: User Resolution Scenarios
    logger.info("\n" + "=" * 60)
    scenarios_ok = await test_user_resolution_scenarios()
    
    # Final Results
    logger.info("\n" + "=" * 60)
    logger.info("🏁 FINAL TEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    logger.info(f"   Basic Webhook: {'✅ PASS' if webhook_ok else '❌ FAIL'}")
    logger.info(f"   User Resolution: {'✅ PASS' if scenarios_ok else '❌ FAIL'}")
    
    all_passed = health_ok and webhook_ok and scenarios_ok
    
    if all_passed:
        logger.info("\n🎉 ALL TESTS PASSED! The Ultimate Stripe Webhook Fix is working!")
        logger.info("   ✅ Webhooks are being received")
        logger.info("   ✅ User resolution is working")
        logger.info("   ✅ Credits are being added")
        logger.info("   ✅ Error handling is robust")
    else:
        logger.error("\n❌ SOME TESTS FAILED. The fix needs more work.")
        logger.error("   Check the logs above for specific issues.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
