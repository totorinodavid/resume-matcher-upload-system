#!/usr/bin/env python3
"""
Quick Credit Check
Verify admin endpoints and check your current credit balance
"""

import asyncio
import httpx
import json

async def quick_credit_check():
    print("🔍 QUICK CREDIT CHECK")
    print("=" * 40)
    print()
    
    backend_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    your_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
    wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            print("Checking admin endpoints availability...")
            
            # Check your balance
            print(f"🔍 Your balance ({your_user_id}):")
            response = await client.get(f"{backend_url}/admin/credits/{your_user_id}")
            if response.status_code == 200:
                balance = response.json()
                print(f"   ✅ Current credits: {balance['total_credits']}")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
            
            print()
            
            # Check wrong user balance
            print(f"🔍 Wrong user balance ({wrong_user_id}):")
            response = await client.get(f"{backend_url}/admin/credits/{wrong_user_id}")
            if response.status_code == 200:
                balance = response.json()
                print(f"   ✅ Available credits: {balance['total_credits']}")
                
                if balance['total_credits'] >= 50:
                    print()
                    print("🚀 READY TO TRANSFER!")
                    print("   The wrong user has enough credits to transfer.")
                    print("   Now executing transfer...")
                    
                    # Execute transfer
                    transfer_request = {
                        "from_user_id": wrong_user_id,
                        "to_user_id": your_user_id,
                        "amount": 50,
                        "reason": "fix_wrong_user_assignment"
                    }
                    
                    response = await client.post(
                        f"{backend_url}/admin/transfer-credits",
                        json=transfer_request
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print("🎉 TRANSFER COMPLETED!")
                        print(f"   Your new balance: {result['to_user_final_balance']} credits")
                        print()
                        print("✅ PROBLEM SOLVED!")
                        print("   Your 50 credits are now available in your account.")
                    else:
                        print(f"❌ Transfer failed: {response.status_code}")
                        print(f"   Response: {response.text}")
                else:
                    print(f"   ❌ Insufficient credits: {balance['total_credits']} < 50")
            else:
                print(f"   ❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(quick_credit_check())
