#!/usr/bin/env python3
"""
Test if the admin endpoint fix is deployed
"""

import asyncio
import httpx

async def test_admin_fix():
    print("🔍 TESTING ADMIN ENDPOINT FIX")
    print("=" * 40)
    print()
    
    backend_url = "https://resume-matcher-backend-j06k.onrender.com"
    test_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print("Testing admin credits endpoint...")
            response = await client.get(f"{backend_url}/admin/credits/{test_user_id}")
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Admin endpoint is working!")
                print(f"Your current balance: {data['total_credits']} credits")
                return True
            else:
                print("❌ Admin endpoint still has issues")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_admin_fix())
    if success:
        print("\n🎉 Ready to run credit transfer!")
    else:
        print("\n⏳ Backend deployment may still be updating...")
