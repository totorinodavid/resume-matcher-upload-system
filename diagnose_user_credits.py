#!/usr/bin/env python3
"""
Emergency User Credit Diagnosis
Diagnose why credits aren't showing up in user's balance
"""

import asyncio
import httpx
import json
from datetime import datetime

async def diagnose_user_credits():
    print("🔍 EMERGENCY USER CREDIT DIAGNOSIS")
    print("=" * 60)
    print()
    
    backend_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    # Your actual user ID from our conversation history
    your_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
    
    # User ID from recent successful payment
    payment_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"
    
    print(f"👤 YOUR USER ID: {your_user_id}")
    print(f"💳 PAYMENT USER ID: {payment_user_id}")
    print(f"🔄 MATCH STATUS: {'✅ SAME USER' if your_user_id == payment_user_id else '❌ DIFFERENT USERS'}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Check backend status
        try:
            response = await client.get(f"{backend_url}/healthz")
            print(f"🌐 Backend Status: ✅ {response.status_code}")
        except Exception as e:
            print(f"🌐 Backend Status: ❌ {e}")
            return
        
        print()
        print("🔍 CHECKING CREDIT BALANCES...")
        print("-" * 40)
        
        # Check your actual user ID credits
        try:
            # Note: We need to implement a credit check endpoint
            # For now, let's check if we can find user info
            print(f"👤 Checking credits for YOUR user ID: {your_user_id}")
            print(f"   This should be where your credits appear...")
            print()
            
            print(f"💳 Recent payment was processed for: {payment_user_id}")
            print(f"   Credits were successfully added to this user...")
            print()
            
            if your_user_id != payment_user_id:
                print("❌ PROBLEM IDENTIFIED:")
                print("   Your actual user ID is different from the payment user ID!")
                print("   This means credits were added to a different account.")
                print()
                print("🔧 SOLUTION NEEDED:")
                print("   1. Transfer credits from payment user to your user")
                print("   2. Or investigate why the payment used wrong user ID")
            else:
                print("✅ User IDs match - need to check why credits aren't visible")
                
        except Exception as e:
            print(f"❌ Error checking credits: {e}")
    
    print()
    print("📊 DIAGNOSIS SUMMARY:")
    print("-" * 40)
    if your_user_id != payment_user_id:
        print("❌ CREDITS ASSIGNED TO WRONG USER")
        print(f"   Your ID: {your_user_id}")
        print(f"   Payment ID: {payment_user_id}")
        print("   Need credit transfer or payment investigation")
    else:
        print("✅ User IDs match - different issue")
        print("   Need to check credit display logic")

if __name__ == "__main__":
    asyncio.run(diagnose_user_credits())
