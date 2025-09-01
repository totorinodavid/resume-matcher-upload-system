#!/usr/bin/env python3
"""
API-Based Credit Transfer
Use the admin API to transfer credits between users
"""

import asyncio
import httpx
import json

async def transfer_credits_via_api():
    print("🔧 API-BASED CREDIT TRANSFER")
    print("=" * 50)
    print()
    
    backend_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    # User IDs from the logs
    wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"
    correct_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
    credits_to_transfer = 50
    
    print(f"TRANSFERRING: {credits_to_transfer} credits")
    print(f"FROM: {wrong_user_id}")
    print(f"TO:   {correct_user_id}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Step 1: Check current balances
            print("🔍 CHECKING CURRENT BALANCES...")
            
            # Check wrong user balance
            response = await client.get(f"{backend_url}/admin/credits/{wrong_user_id}")
            if response.status_code == 200:
                wrong_balance = response.json()
                print(f"Wrong user balance: {wrong_balance['total_credits']}")
            else:
                print(f"❌ Failed to get wrong user balance: {response.status_code}")
                print(f"Response: {response.text}")
                return
            
            # Check correct user balance
            response = await client.get(f"{backend_url}/admin/credits/{correct_user_id}")
            if response.status_code == 200:
                correct_balance = response.json()
                print(f"Your current balance: {correct_balance['total_credits']}")
            else:
                print(f"❌ Failed to get your balance: {response.status_code}")
                print(f"Response: {response.text}")
                return
            
            print()
            
            # Step 2: Transfer credits
            if wrong_balance['total_credits'] >= credits_to_transfer:
                print("✅ Transfer conditions met. Executing...")
                
                transfer_request = {
                    "from_user_id": wrong_user_id,
                    "to_user_id": correct_user_id,
                    "amount": credits_to_transfer,
                    "reason": "fix_wrong_user_assignment"
                }
                
                response = await client.post(
                    f"{backend_url}/admin/transfer-credits",
                    json=transfer_request
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("🎉 TRANSFER COMPLETED!")
                    print(f"   Transferred: {result['transferred']} credits")
                    print(f"   Your new balance: {result['to_user_final_balance']}")
                    print(f"   Wrong user final balance: {result['from_user_final_balance']}")
                else:
                    print(f"❌ Transfer failed: {response.status_code}")
                    print(f"Response: {response.text}")
            else:
                print(f"❌ Insufficient credits: {wrong_balance['total_credits']} < {credits_to_transfer}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(transfer_credits_via_api())
