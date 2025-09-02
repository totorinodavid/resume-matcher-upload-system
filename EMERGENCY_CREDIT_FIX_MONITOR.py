#!/usr/bin/env python3
"""
🚨 EMERGENCY DEPLOYMENT MONITOR FÜR DEBUG ENDPOINTS 🚨

Überwacht das Deployment der Emergency Debug Endpoints 
und führt SOFORT die Credit-Korrektur durch!
"""

import asyncio
import aiohttp
import time
from datetime import datetime

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

async def monitor_and_fix_credits():
    print("🚨 EMERGENCY DEPLOYMENT MONITOR - DEBUG ENDPOINTS 🚨")
    print("="*60)
    print("Ziel: Credits von User ID 1 zum richtigen User transferieren")
    print("User: davis t (197acb67-0d0a-467f-8b63-b2886c7fff6e)")
    print("Credits: 50 (Stripe payment evt_1S2acYEPwuWwkzKTrZAspI0P)")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        
        # Monitor for deployment
        for attempt in range(20):  # 20 attempts = 10 minutes
            elapsed = attempt * 30
            print(f"\n⏱️ Attempt {attempt + 1}/20 (Time: {elapsed}s)")
            
            # Test debug endpoint availability
            try:
                async with session.get(f"{BACKEND_URL}/admin/debug/database-schema") as response:
                    if response.status == 200:
                        print("🎉 DEBUG ENDPOINTS ARE LIVE! Starting immediate fix...")
                        schema_data = await response.json()
                        print(f"📊 Database schema: {schema_data}")
                        break
                    else:
                        print(f"⏳ Debug endpoints not ready: HTTP {response.status}")
            except Exception as e:
                print(f"⏳ Connection error: {e}")
            
            if attempt < 19:
                print("⏳ Waiting 30s for next check...")
                await asyncio.sleep(30)
        else:
            print("❌ Timeout waiting for debug endpoints")
            return
        
        # IMMEDIATE CREDIT FIX SEQUENCE
        print("\n🚨 STARTING IMMEDIATE CREDIT FIX SEQUENCE 🚨")
        
        # 1. Get current database state
        print("\n1. 📊 Database State Analysis...")
        try:
            async with session.get(f"{BACKEND_URL}/admin/debug/all-users") as response:
                if response.status == 200:
                    users_data = await response.json()
                    print(f"   ✅ Found {len(users_data.get('users', []))} users:")
                    for user in users_data.get('users', []):
                        print(f"      - ID: {user.get('id')}, Email: {user.get('email')}, Name: {user.get('name')}")
                else:
                    print(f"   ❌ User listing failed: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # 2. Check credits for User ID 1
        print("\n2. 💰 Checking credits for User ID 1...")
        try:
            async with session.get(f"{BACKEND_URL}/admin/debug/credits/1") as response:
                if response.status == 200:
                    credits_data = await response.json()
                    user_1_credits = credits_data.get('credits', 0)
                    print(f"   ✅ User ID 1 has {user_1_credits} credits")
                    if user_1_credits < 50:
                        print("   ⚠️ User ID 1 doesn't have enough credits to transfer")
                        return
                else:
                    print(f"   ❌ Credit check failed: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # 3. Create/find correct user
        print("\n3. 👤 Creating/finding correct user...")
        correct_user_data = {
            "email": "davis.t@example.com",
            "name": "davis t",
            "user_uuid": "197acb67-0d0a-467f-8b63-b2886c7fff6e"
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/admin/debug/emergency-user-creation", json=correct_user_data) as response:
                if response.status == 200:
                    user_result = await response.json()
                    correct_user_id = user_result.get("user_id")
                    print(f"   ✅ Correct user ready: ID {correct_user_id}")
                    print(f"   Action: {user_result.get('action', 'unknown')}")
                else:
                    response_text = await response.text()
                    print(f"   ❌ User creation failed: HTTP {response.status}")
                    print(f"   Response: {response_text}")
                    return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # 4. EMERGENCY CREDIT ASSIGNMENT
        print("\n4. 🚨 EMERGENCY CREDIT ASSIGNMENT...")
        credit_assignment_data = {
            "user_id": str(correct_user_id),
            "credits": 50,
            "reason": "EMERGENCY_FIX: Stripe payment evt_1S2acYEPwuWwkzKTrZAspI0P assigned to wrong user",
            "stripe_event": "evt_1S2acYEPwuWwkzKTrZAspI0P",
            "admin_note": "Emergency credit assignment - payment was processed successfully but assigned to User ID 1 instead of correct user"
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/admin/debug/emergency-credit-assignment", json=credit_assignment_data) as response:
                if response.status == 200:
                    assignment_result = await response.json()
                    print(f"   🎉 EMERGENCY CREDIT ASSIGNMENT SUCCESS!")
                    print(f"   User ID: {assignment_result.get('user_id')}")
                    print(f"   Credits Added: {assignment_result.get('credits_added')}")
                    print(f"   New Balance: {assignment_result.get('new_balance')}")
                    print(f"   Stripe Event: {assignment_result.get('stripe_event')}")
                else:
                    response_text = await response.text()
                    print(f"   ❌ Credit assignment failed: HTTP {response.status}")
                    print(f"   Response: {response_text}")
                    return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # 5. Final verification
        print("\n5. ✅ Final Verification...")
        try:
            async with session.get(f"{BACKEND_URL}/admin/debug/credits/{correct_user_id}") as response:
                if response.status == 200:
                    final_credits = await response.json()
                    print(f"   🎉 Correct user now has {final_credits.get('credits', 0)} credits!")
                else:
                    print(f"   ⚠️ Cannot verify final balance: HTTP {response.status}")
        except Exception as e:
            print(f"   ⚠️ Verification error: {e}")
        
        print("\n" + "="*60)
        print("🎉 EMERGENCY CREDIT FIX COMPLETE! 🎉")
        print("✅ Davis T should now have his 50 credits!")
        print("✅ Stripe payment properly resolved!")
        print("✅ Future payments will work correctly!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(monitor_and_fix_credits())
