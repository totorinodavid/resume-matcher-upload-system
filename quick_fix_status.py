#!/usr/bin/env python3
"""
SCHNELLER STATUS CHECK für den Critical Fix
"""

import asyncio
import aiohttp
import json

async def quick_status_check():
    BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"
    
    async with aiohttp.ClientSession() as session:
        # Test the webhook endpoint
        test_payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_fix_check",
                    "payment_status": "paid",
                    "customer": "cus_test",
                    "metadata": {
                        "user_id": "test_user",
                        "credits": "10"
                    }
                }
            }
        }
        
        try:
            async with session.post(
                f"{BACKEND_URL}/webhooks/stripe",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            ) as response:
                status = response.status
                text = await response.text()
                
                print(f"🪝 Webhook Test Status: {status}")
                
                if status == 500:
                    if "ImportError" in text and "_resolve_user_id_BULLETPROOF" in text:
                        print("❌ ImportError STILL EXISTS - Deployment not complete")
                        print("⏳ Waiting for new deployment...")
                    else:
                        print("⚠️  Different 500 error:")
                        print(text[:300] + "..." if len(text) > 300 else text)
                elif status in [200, 202]:
                    print("✅ WEBHOOK WORKING - ImportError FIXED!")
                    print("🎉 Critical fix deployed successfully!")
                    print("💳 Credits can now be assigned!")
                else:
                    print(f"❓ Unexpected status: {status}")
                    print(text[:200] + "..." if len(text) > 200 else text)
                
        except Exception as e:
            print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("🚨 QUICK STATUS CHECK - Critical Fix Deployment")
    print("="*50)
    asyncio.run(quick_status_check())
