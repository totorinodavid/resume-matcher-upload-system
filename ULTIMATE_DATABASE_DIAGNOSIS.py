#!/usr/bin/env python3
"""
🚨 ULTIMATE DATABASE REALITY CHECK 🚨

Finde heraus was WIRKLICH in der Database ist und löse das Credit-Problem SOFORT!
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

async def ultimate_database_diagnosis():
    print("🚨 ULTIMATE DATABASE REALITY CHECK 🚨")
    print("="*60)
    print("Das Problem: Credits gehen an falschen User!")
    print("Die Lösung: Database-Realität verstehen und Credits richtig zuweisen!")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Database Schema Discovery
        print("\n1. 📊 Database Schema Discovery...")
        try:
            async with session.get(f"{BACKEND_URL}/api/v1/debug/database-schema") as response:
                if response.status == 200:
                    schema_data = await response.json()
                    print(f"   ✅ Schema discovered: {schema_data}")
                else:
                    print(f"   ⚠️ Schema endpoint not available: HTTP {response.status}")
        except Exception as e:
            print(f"   ⚠️ Schema discovery failed: {e}")
        
        # 2. List ALL users in database
        print("\n2. 👥 All Users in Database...")
        try:
            async with session.get(f"{BACKEND_URL}/api/v1/debug/all-users") as response:
                if response.status == 200:
                    users_data = await response.json()
                    print(f"   ✅ Found {len(users_data.get('users', []))} users:")
                    for user in users_data.get('users', []):
                        print(f"      - ID: {user.get('id')}, Email: {user.get('email')}, Name: {user.get('name')}")
                else:
                    print(f"   ⚠️ Users endpoint not available: HTTP {response.status}")
        except Exception as e:
            print(f"   ⚠️ Users listing failed: {e}")
        
        # 3. Check credits for User ID 1 (who got the credits)
        print("\n3. 💰 Credit Check for User ID 1...")
        try:
            async with session.get(f"{BACKEND_URL}/api/v1/debug/credits/1") as response:
                if response.status == 200:
                    credits_data = await response.json()
                    print(f"   ✅ User ID 1 credits: {credits_data}")
                else:
                    print(f"   ⚠️ Credits endpoint not available: HTTP {response.status}")
        except Exception as e:
            print(f"   ⚠️ Credits check failed: {e}")
        
        # 4. Search for the correct user by email/name
        print("\n4. 🔍 Search for 'davis t'...")
        search_terms = ["davis", "davis t", "197acb67-0d0a-467f-8b63-b2886c7fff6e"]
        
        for term in search_terms:
            try:
                async with session.get(f"{BACKEND_URL}/api/v1/debug/search-users?q={term}") as response:
                    if response.status == 200:
                        search_data = await response.json()
                        print(f"   🔍 Search '{term}': {search_data}")
                    else:
                        print(f"   ⚠️ Search '{term}' failed: HTTP {response.status}")
            except Exception as e:
                print(f"   ⚠️ Search '{term}' error: {e}")
        
        # 5. EMERGENCY: Direct credit assignment to correct user
        print("\n5. 🚨 EMERGENCY CREDIT ASSIGNMENT...")
        
        # First, try to find or create the correct user
        correct_user_data = {
            "email": "davis.t@example.com",  # From logs 
            "name": "davis t",  # From logs
            "user_uuid": "197acb67-0d0a-467f-8b63-b2886c7fff6e"  # The UUID from payments
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/api/v1/debug/emergency-user-creation", json=correct_user_data) as response:
                if response.status == 200:
                    user_creation_result = await response.json()
                    print(f"   ✅ User creation/lookup: {user_creation_result}")
                    
                    # Now assign credits to the correct user
                    target_user_id = user_creation_result.get("user_id") or user_creation_result.get("id")
                    if target_user_id:
                        credit_assignment_data = {
                            "user_id": target_user_id,
                            "credits": 50,
                            "reason": "EMERGENCY_FIX: Stripe payment evt_1S2acYEPwuWwkzKTrZAspI0P",
                            "stripe_event": "evt_1S2acYEPwuWwkzKTrZAspI0P",
                            "admin_note": "Emergency credit assignment - payment was processed but assigned to wrong user ID 1"
                        }
                        
                        async with session.post(f"{BACKEND_URL}/api/v1/debug/emergency-credit-assignment", json=credit_assignment_data) as credit_response:
                            if credit_response.status == 200:
                                credit_result = await credit_response.json()
                                print(f"   🎉 EMERGENCY CREDIT ASSIGNMENT SUCCESS: {credit_result}")
                            else:
                                credit_text = await credit_response.text()
                                print(f"   ❌ Credit assignment failed: HTTP {credit_response.status}")
                                print(f"   Response: {credit_text}")
                else:
                    creation_text = await response.text()
                    print(f"   ❌ User creation failed: HTTP {response.status}")
                    print(f"   Response: {creation_text}")
                    
        except Exception as e:
            print(f"   ❌ Emergency assignment error: {e}")
        
        print("\n" + "="*60)
        print("🎯 DIAGNOSIS COMPLETE")
        print("If debug endpoints don't exist, we need to:")
        print("1. Create proper admin endpoints")
        print("2. Fix the UltraEmergencyUserService to find existing users")  
        print("3. Implement credit transfer functionality")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(ultimate_database_diagnosis())
