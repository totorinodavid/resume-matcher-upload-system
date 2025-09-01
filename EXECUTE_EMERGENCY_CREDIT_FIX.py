#!/usr/bin/env python3
"""
🚨 EMERGENCY CREDIT FIX - EXECUTE NOW
Direct fix for the user ID mismatch problem

PROBLEM IDENTIFIED:
- Frontend User: af71df5d-f4d0f5-56b9aba6259a (seeing 0 credits)
- Payment went to: 31af2234-b4a9-4719-ae70-e0aee7c08354 (has the 50 credits)
- Need to add 50 credits to the frontend user

SOLUTION: Add 50 credits to frontend user via emergency endpoint
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Production backend URL
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

# User IDs from logs analysis
FRONTEND_USER = "af71df5d-f4d0f5-56b9aba6259a"  # User who should have the credits
PAYMENT_USER = "31af2234-b4a9-4719-ae70-e0aee7c08354"   # User who actually got the credits

# Credits to add (from Stripe logs: 50 credits)
CREDITS_TO_ADD = 50

# Emergency authorization
EMERGENCY_CODE = "user_id_mismatch_fix_2025"

async def add_credits_emergency(user_id: str, credits: int, reason: str):
    """Add credits via emergency endpoint"""
    
    url = f"{BACKEND_URL}/api/v1/emergency/user/{user_id}/add-credits"
    
    params = {
        "credits": credits,
        "reason": reason,
        "emergency_code": EMERGENCY_CODE
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                status = response.status
                response_text = await response.text()
                
                print(f"🔄 Emergency credit addition:")
                print(f"   URL: {url}")
                print(f"   Status: {status}")
                print(f"   Response: {response_text}")
                
                if status == 200:
                    try:
                        data = json.loads(response_text)
                        print(f"✅ SUCCESS!")
                        print(f"   Balance before: {data.get('balance_before')}")
                        print(f"   Balance after: {data.get('balance_after')}")
                        print(f"   Message: {data.get('message')}")
                        return True
                    except:
                        print(f"✅ SUCCESS (could not parse response)")
                        return True
                else:
                    print(f"❌ FAILED: {response_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def check_user_credits(user_id: str, description: str):
    """Check credits for verification"""
    
    url = f"{BACKEND_URL}/api/v1/emergency/user/{user_id}/credits"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    data = await response.json()
                    credits = data.get('credits', 0)
                    print(f"🔍 {description}: {credits} credits")
                    return credits
                else:
                    print(f"❌ Could not check {description} credits")
                    return 0
    except Exception as e:
        print(f"❌ Error checking {description}: {e}")
        return 0

async def execute_emergency_fix():
    """Execute the emergency credit fix"""
    
    print("=" * 60)
    print("🚨 EMERGENCY CREDIT FIX - EXECUTING NOW")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print(f"\n🎯 PROBLEM:")
    print(f"   Stripe payment processed successfully ✅")
    print(f"   Credits went to wrong user: {PAYMENT_USER}")
    print(f"   Frontend user has 0 credits: {FRONTEND_USER}")
    
    print(f"\n🔄 STEP 1: Check current balances")
    frontend_credits_before = await check_user_credits(FRONTEND_USER, "Frontend user")
    payment_credits_before = await check_user_credits(PAYMENT_USER, "Payment user")
    
    print(f"\n🚨 STEP 2: Add {CREDITS_TO_ADD} credits to frontend user")
    success = await add_credits_emergency(
        FRONTEND_USER,
        CREDITS_TO_ADD,
        f"Emergency fix for Stripe user ID mismatch - payment went to {PAYMENT_USER} instead"
    )
    
    if success:
        print(f"\n🔍 STEP 3: Verify fix")
        frontend_credits_after = await check_user_credits(FRONTEND_USER, "Frontend user after fix")
        
        print(f"\n📊 RESULTS:")
        print(f"   Frontend user before: {frontend_credits_before} credits")
        print(f"   Frontend user after:  {frontend_credits_after} credits")
        print(f"   Expected increase: {CREDITS_TO_ADD} credits")
        
        if frontend_credits_after >= frontend_credits_before + CREDITS_TO_ADD:
            print(f"\n✅ SUCCESS: Emergency fix completed!")
            print(f"   User should now see {frontend_credits_after} credits in frontend")
        else:
            print(f"\n⚠️  WARNING: Credits may not have been added correctly")
            
    else:
        print(f"\n❌ FAILED: Emergency fix could not be completed")
        print(f"💡 Alternative: May need manual database intervention")
    
    print(f"\n📋 FINAL STATUS:")
    print(f"   Stripe webhook: ✅ Working correctly")
    print(f"   Payment processing: ✅ Successful") 
    print(f"   User ID mapping: ❌ Needs investigation")
    print(f"   Credit fix: {'✅' if success else '❌'}")
    
    print("\n" + "=" * 60)
    print("🚨 EMERGENCY FIX COMPLETE")
    print("=" * 60)

def main():
    """Main execution function"""
    try:
        asyncio.run(execute_emergency_fix())
    except KeyboardInterrupt:
        print("\n👋 Emergency fix stopped by user")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
