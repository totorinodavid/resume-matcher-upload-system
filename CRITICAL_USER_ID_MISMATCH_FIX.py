#!/usr/bin/env python3
"""
🚨 CRITICAL USER ID MISMATCH DIAGNOSTIC
The webhook processed successfully but credits went to wrong user!

PROBLEM IDENTIFIED:
- Frontend User: af71df5d-f***f5-56b9aba6259a
- Payment User:  31af2234-b4a9-4719-ae70-e0aee7c08354
- Credits added to payment user, not frontend user!

This script will:
1. Verify which user actually has the credits
2. Check if there's a user mapping issue  
3. Transfer credits to correct user if needed
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

# User IDs from logs
FRONTEND_USER = "af71df5d-f4d0f5-56b9aba6259a"  # User seeing 0 credits
PAYMENT_USER = "31af2234-b4a9-4719-ae70-e0aee7c08354"   # User who got credits

async def check_user_credits(user_id: str, description: str):
    """Check credits for a specific user"""
    url = f"{BACKEND_URL}/api/v1/debug/user/{user_id}/credits"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                status = response.status
                response_text = await response.text()
                
                print(f"🔍 {description} ({user_id}):")
                print(f"   Status: {status}")
                print(f"   Response: {response_text}")
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        credits = data.get('credits', 'unknown')
                        print(f"   💰 Credits: {credits}")
                        return credits
                    except:
                        print(f"   ⚠️  Could not parse response")
                        return None
                else:
                    print(f"   ❌ Failed to get credits")
                    return None
                    
    except Exception as e:
        print(f"❌ Error checking {description}: {e}")
        return None

async def transfer_credits_if_needed():
    """Check both users and transfer credits if needed"""
    
    print("=" * 60)
    print("🚨 CRITICAL USER ID MISMATCH DIAGNOSTIC")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n🎯 PROBLEM IDENTIFIED:")
    print(f"   Frontend User: {FRONTEND_USER} (seeing 0 credits)")
    print(f"   Payment User:  {PAYMENT_USER} (got the 50 credits)")
    print("\n🔍 CHECKING CREDIT BALANCES:")
    
    # Check credits for both users
    frontend_credits = await check_user_credits(FRONTEND_USER, "Frontend User")
    payment_credits = await check_user_credits(PAYMENT_USER, "Payment User")
    
    print(f"\n📊 RESULTS:")
    print(f"   Frontend User Credits: {frontend_credits}")
    print(f"   Payment User Credits:  {payment_credits}")
    
    # Determine action needed
    if payment_credits and int(payment_credits) > 0 and (not frontend_credits or int(frontend_credits) == 0):
        print(f"\n🎯 SOLUTION NEEDED:")
        print(f"   ✅ Payment user has {payment_credits} credits")
        print(f"   ❌ Frontend user has {frontend_credits} credits")
        print(f"   🔧 ACTION: Transfer {payment_credits} credits from payment user to frontend user")
        
        # Here we would implement the transfer logic
        print(f"\n🚨 MANUAL ACTION REQUIRED:")
        print(f"   1. Connect to database")
        print(f"   2. Transfer {payment_credits} credits from {PAYMENT_USER} to {FRONTEND_USER}")
        print(f"   3. Update user mapping to prevent future issues")
        
    else:
        print(f"\n💡 STATUS: Credit distribution appears normal")
    
    print("\n" + "=" * 60)
    print("🔍 DIAGNOSTIC COMPLETE")
    print("=" * 60)

def main():
    """Main function"""
    try:
        asyncio.run(transfer_credits_if_needed())
    except KeyboardInterrupt:
        print("\n👋 Diagnostic stopped by user")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
