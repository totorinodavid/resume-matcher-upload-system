#!/usr/bin/env python3
"""
🚨 STRIPE PAYMENT VERIFICATION & CREDIT HUNT 🚨

Überprüft den aktuellen Status der Stripe Zahlung
und findet heraus wo die Credits sind!
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

async def hunt_missing_credits():
    print("🚨 CREDIT HUNT - WO SIND DIE 50 CREDITS? 🚨")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Check all users and their credits
        print("1. 🔍 Checking ALL users and their credits...")
        try:
            async with session.get(f"{BACKEND_URL}/admin/debug/all-users") as response:
                if response.status == 200:
                    users_data = await response.json()
                    users = users_data.get('users', [])
                    
                    for user in users:
                        user_id = user.get('id')
                        print(f"\n   User ID: {user_id}")
                        print(f"   Email: {user.get('email')}")
                        print(f"   Name: {user.get('name')}")
                        
                        # Check credits for this user
                        try:
                            async with session.get(f"{BACKEND_URL}/admin/debug/credits/{user_id}") as credit_response:
                                if credit_response.status == 200:
                                    credit_data = await credit_response.json()
                                    credits = credit_data.get('credits', 0)
                                    print(f"   💰 Credits: {credits}")
                                    
                                    if credits > 0:
                                        print(f"   🎯 FOUND CREDITS! This user has {credits} credits!")
                                else:
                                    print(f"   ❌ Cannot check credits: HTTP {credit_response.status}")
                        except Exception as e:
                            print(f"   ❌ Credit check error: {e}")
                else:
                    print(f"❌ Cannot get users: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"❌ Error getting users: {e}")
            return
        
        # 2. Search for user with target UUID
        print("\n2. 🔍 Searching for target UUID...")
        try:
            search_data = {"search_term": "197acb67-0d0a-467f-8b63-b2886c7fff6e"}
            async with session.post(f"{BACKEND_URL}/admin/debug/search-users", json=search_data) as response:
                if response.status == 200:
                    search_result = await response.json()
                    print(f"   Search result: {search_result}")
                else:
                    print(f"   ❌ Search failed: HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ Search error: {e}")
        
        # 3. Check webhook logs to see what happened
        print("\n3. 📋 Checking recent webhook activity...")
        try:
            # Try to get any webhook-related info
            test_webhook_data = {
                "type": "payment_intent.succeeded",
                "data": {
                    "object": {
                        "id": "pi_test_check",
                        "metadata": {
                            "user_id": "197acb67-0d0a-467f-8b63-b2886c7fff6e",
                            "credits": "50"
                        }
                    }
                }
            }
            
            print("   Testing webhook endpoint with metadata...")
            async with session.post(f"{BACKEND_URL}/webhooks/stripe/emergency", 
                                  json=test_webhook_data,
                                  headers={"Content-Type": "application/json"}) as response:
                webhook_result = await response.text()
                print(f"   Webhook test result: HTTP {response.status}")
                print(f"   Response: {webhook_result}")
                
        except Exception as e:
            print(f"   ❌ Webhook test error: {e}")
        
        print("\n" + "="*60)
        print("🔍 CREDIT HUNT COMPLETE")
        print("Next: Analyze results and assign credits correctly")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(hunt_missing_credits())
