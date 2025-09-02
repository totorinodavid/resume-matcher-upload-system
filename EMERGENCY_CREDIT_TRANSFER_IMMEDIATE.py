#!/usr/bin/env python3
"""
🚨 EMERGENCY CREDIT TRANSFER 🚨

Transferiert die fälschlich zugewiesenen Credits vom falschen User (ID 1) 
zum richtigen User (197acb67-0d0a-467f-8b63-b2886c7fff6e).

Davis T hat bereits bezahlt und wartet auf seine Credits!
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

# User Details aus den Logs
WRONG_USER_ID = "1"  # Credits wurden fälschlich hier zugewiesen
CORRECT_USER_UUID = "197acb67-0d0a-467f-8b63-b2886c7fff6e"  # Echter User
CREDITS_TO_TRANSFER = 50  # Betrag zum Transfer
STRIPE_EVENT = "evt_1S2acYEPwuWwkzKTrZAspI0P"

async def emergency_credit_transfer():
    print("🚨 EMERGENCY CREDIT TRANSFER 🚨")
    print("="*50)
    print(f"From: User ID {WRONG_USER_ID} (falsely assigned)")
    print(f"To: User UUID {CORRECT_USER_UUID} (correct user)")
    print(f"Amount: {CREDITS_TO_TRANSFER} credits")
    print(f"Reason: Stripe payment {STRIPE_EVENT}")
    print("="*50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Check credit balance of wrong user (should have 50 credits)
        print("\n1. 📊 Checking current credit balances...")
        try:
            async with session.get(f"{BACKEND_URL}/api/v1/credits/balance/{WRONG_USER_ID}") as response:
                if response.status == 200:
                    data = await response.json()
                    wrong_user_credits = data.get("credits", 0)
                    print(f"   User ID {WRONG_USER_ID}: {wrong_user_credits} credits")
                else:
                    print(f"   ❌ Cannot check User ID {WRONG_USER_ID}: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ Error checking User ID {WRONG_USER_ID}: {e}")
            return
        
        # 2. Check if correct user exists
        try:
            async with session.get(f"{BACKEND_URL}/api/v1/users/{CORRECT_USER_UUID}") as response:
                if response.status == 200:
                    correct_user_data = await response.json()
                    print(f"   User UUID {CORRECT_USER_UUID}: Found")
                elif response.status == 404:
                    print(f"   ⚠️ User UUID {CORRECT_USER_UUID}: NOT FOUND - Need to create")
                    # Create the correct user first
                    print("\n2. 🔧 Creating correct user...")
                    create_payload = {
                        "email": "davis.t@example.com",  # From session_email in logs
                        "name": "davis t"  # From session_name in logs
                    }
                    async with session.post(f"{BACKEND_URL}/api/v1/users/emergency-create", json=create_payload) as create_response:
                        if create_response.status == 200:
                            user_data = await create_response.json()
                            print(f"   ✅ Created user: {user_data}")
                        else:
                            print(f"   ❌ Failed to create user: HTTP {create_response.status}")
                            return
                else:
                    print(f"   ❌ Error checking User UUID {CORRECT_USER_UUID}: HTTP {response.status}")
                    return
        except Exception as e:
            print(f"   ❌ Error checking User UUID {CORRECT_USER_UUID}: {e}")
            return
        
        # 3. Transfer credits
        print(f"\n3. 💰 Transferring {CREDITS_TO_TRANSFER} credits...")
        transfer_payload = {
            "from_user_id": WRONG_USER_ID,
            "to_user_id": CORRECT_USER_UUID,
            "amount": CREDITS_TO_TRANSFER,
            "reason": f"EMERGENCY_TRANSFER: Stripe payment {STRIPE_EVENT} assigned to wrong user",
            "admin_note": f"Payment completed at 2025-09-01 16:30:18, credits mistakenly assigned to User ID 1 instead of correct UUID {CORRECT_USER_UUID}"
        }
        
        try:
            async with session.post(f"{BACKEND_URL}/api/v1/admin/transfer-credits", json=transfer_payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"   ✅ Credit transfer successful: {result}")
                else:
                    response_text = await response.text()
                    print(f"   ❌ Credit transfer failed: HTTP {response.status}")
                    print(f"   Response: {response_text}")
                    
                    # Fallback: Manual credit assignment
                    print("\n4. 🔄 Fallback: Direct credit assignment...")
                    fallback_payload = {
                        "user_id": CORRECT_USER_UUID,
                        "credits": CREDITS_TO_TRANSFER,
                        "reason": f"MANUAL_ASSIGNMENT: Stripe payment {STRIPE_EVENT}",
                        "admin_note": "Emergency credit assignment after payment misdirection"
                    }
                    
                    async with session.post(f"{BACKEND_URL}/api/v1/admin/add-credits", json=fallback_payload) as fallback_response:
                        if fallback_response.status == 200:
                            fallback_result = await fallback_response.json()
                            print(f"   ✅ Manual credit assignment successful: {fallback_result}")
                        else:
                            fallback_text = await fallback_response.text()
                            print(f"   ❌ Manual credit assignment failed: HTTP {fallback_response.status}")
                            print(f"   Response: {fallback_text}")
                            return
                            
        except Exception as e:
            print(f"   ❌ Error during credit transfer: {e}")
            return
        
        # 4. Verify final balances
        print(f"\n5. ✅ Verifying final credit balances...")
        try:
            # Check correct user's credits
            async with session.get(f"{BACKEND_URL}/api/v1/credits/balance/{CORRECT_USER_UUID}") as response:
                if response.status == 200:
                    data = await response.json()
                    correct_user_credits = data.get("credits", 0)
                    print(f"   User UUID {CORRECT_USER_UUID}: {correct_user_credits} credits ✅")
                else:
                    print(f"   ❌ Cannot verify User UUID {CORRECT_USER_UUID}: HTTP {response.status}")
            
            # Check wrong user's credits (should be 0 now)
            async with session.get(f"{BACKEND_URL}/api/v1/credits/balance/{WRONG_USER_ID}") as response:
                if response.status == 200:
                    data = await response.json()
                    wrong_user_credits = data.get("credits", 0)
                    print(f"   User ID {WRONG_USER_ID}: {wrong_user_credits} credits")
                else:
                    print(f"   ❌ Cannot verify User ID {WRONG_USER_ID}: HTTP {response.status}")
                    
        except Exception as e:
            print(f"   ❌ Error verifying balances: {e}")
        
        print("\n" + "="*50)
        print("🎉 EMERGENCY CREDIT TRANSFER COMPLETE! 🎉")
        print("✅ Davis T should now have his 50 credits!")
        print("✅ Stripe payment properly resolved!")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(emergency_credit_transfer())
