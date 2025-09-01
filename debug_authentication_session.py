#!/usr/bin/env python3
"""
Debug Authentication Session
Find out why wrong user ID is being sent to Stripe
"""

import asyncio
import httpx
import json
from datetime import datetime

async def debug_auth_session():
    print("🔍 AUTHENTICATION SESSION DEBUG")
    print("=" * 60)
    print()
    
    print("PROBLEM ANALYSIS:")
    print("-" * 30)
    print("✅ Payments are processed successfully")
    print("✅ Credits are added to database") 
    print("❌ Credits go to WRONG user ID")
    print()
    print("USER ID MISMATCH:")
    print(f"   Your actual ID: e747de39-1b54-4cd0-96eb-e68f155931e2")
    print(f"   Payment ID:     7675e93c-341b-412d-a41c-cfe1dc519172")
    print()
    
    print("ROOT CAUSE INVESTIGATION:")
    print("-" * 30)
    print("The problem is in the frontend authentication session.")
    print("When you create a Stripe checkout, the wrong user ID")
    print("is being passed from the authentication session.")
    print()
    
    print("POSSIBLE CAUSES:")
    print("1. Multiple user accounts - you might be logged in with different ID")
    print("2. Authentication token corruption or old session data")
    print("3. Browser session caching old user ID")
    print("4. NextAuth session returning wrong user data")
    print()
    
    print("IMMEDIATE SOLUTIONS:")
    print("-" * 30)
    print("OPTION A: Fix the authentication (recommended)")
    print("   1. Clear browser cache and cookies")
    print("   2. Log out completely and log back in")
    print("   3. Check which user ID appears in the frontend")
    print()
    
    print("OPTION B: Transfer existing credits")
    print("   1. Move the 50 credits from wrong user to your user")
    print("   2. Quick database operation to fix this specific case")
    print()
    
    print("OPTION C: Fix future payments")
    print("   1. Add frontend validation to ensure correct user ID")
    print("   2. Add warning if user ID doesn't match expected pattern")
    print()
    
    backend_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    print("DIAGNOSTIC QUESTIONS:")
    print("-" * 30)
    print("1. When you log into the frontend, what user ID do you see?")
    print("2. Have you created multiple accounts with different emails?")
    print("3. Are you using the same email/login method each time?")
    print("4. Do you see your correct email in the payment metadata?")
    print()
    
    print("TECHNICAL ANALYSIS:")
    print("-" * 30)
    print("The Stripe metadata shows:")
    print('   "session_email": "<email>"')
    print('   "session_name": "davis t"')
    print('   "user_id": "7675e93c-341b-412d-a41c-cfe1dc519172"')
    print()
    print("This suggests you are logged in, but with a different user ID")
    print("than expected. This could happen if:")
    print("- You have multiple accounts")
    print("- Your session is corrupted")
    print("- The frontend is caching old authentication data")

if __name__ == "__main__":
    asyncio.run(debug_auth_session())
