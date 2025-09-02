#!/usr/bin/env python3
"""
🚨 DIRECT CREDIT ASSIGNMENT 🚨
Direkte Credit-Zuweisung für davis t
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

async def assign_credits_directly():
    print("🚨 DIRECT CREDIT ASSIGNMENT FOR DAVIS T 🚨")
    print("="*50)
    
    async with aiohttp.ClientSession() as session:
        
        # Create/ensure correct user exists
        print("1. 👤 Creating correct user...")
        user_data = {
            "email": "davis.t@example.com",
            "name": "davis t", 
            "user_uuid": "197acb67-0d0a-467f-8b63-b2886c7fff6e"
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/admin/debug/emergency-user-creation", json=user_data) as response:
                print(f"User creation status: {response.status}")
                result = await response.text()
                print(f"Response: {result}")
                
                if response.status == 200:
                    user_result = json.loads(result)
                    correct_user_id = user_result.get("user_id")
                    print(f"✅ User ready: ID {correct_user_id}")
                else:
                    print("❌ User creation failed")
                    return
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Assign credits directly
        print(f"\n2. 💰 Assigning 50 credits to user {correct_user_id}...")
        credit_data = {
            "user_id": str(correct_user_id),
            "credits": 50,
            "reason": "Stripe payment evt_1S2acYEPwuWwkzKTrZAspI0P - davis t payment",
            "stripe_event": "evt_1S2acYEPwuWwkzKTrZAspI0P",
            "admin_note": "Direct assignment for davis t - Stripe payment processed"
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/admin/debug/emergency-credit-assignment", json=credit_data) as response:
                print(f"Credit assignment status: {response.status}")
                result = await response.text()
                print(f"Response: {result}")
                
                if response.status == 200:
                    print("🎉 CREDITS ASSIGNED SUCCESSFULLY!")
                else:
                    print("❌ Credit assignment failed")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n✅ DONE - davis t should now have his credits!")

if __name__ == "__main__":
    asyncio.run(assign_credits_directly())
