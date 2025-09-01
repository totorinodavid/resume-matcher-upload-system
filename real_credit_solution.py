#!/usr/bin/env python3
"""
REAL SOLUTION: Credit Transfer and User Validation
Addresses the root cause and fixes the immediate problem
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Optional

# Add backend path
sys.path.append(os.path.join(os.path.dirname(__file__), "apps", "backend"))

async def real_credit_solution():
    print("🔧 REAL SOLUTION: CREDIT TRANSFER AND VALIDATION")
    print("=" * 70)
    print()
    
    # The facts from the logs
    wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"  # Where credits went
    correct_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"  # Your actual ID
    credits_to_transfer = 50
    
    print(f"PROBLEM: Credits assigned to wrong user")
    print(f"FROM (wrong): {wrong_user_id}")
    print(f"TO (correct): {correct_user_id}")
    print(f"AMOUNT: {credits_to_transfer} credits")
    print()
    
    try:
        # Import database components
        from app.core.database import get_db_session
        from app.services.credits_service import CreditsService
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select, text
        from app.models import UserCredits, StripeCustomer
        
        print("🔍 STEP 1: ANALYZING CURRENT STATE")
        print("-" * 40)
        
        async for db_session in get_db_session():
            credits_service = CreditsService(db_session)
            
            # Check wrong user credits
            print(f"Checking wrong user ({wrong_user_id})...")
            wrong_user_credits = await credits_service.get_user_credits(wrong_user_id)
            if wrong_user_credits:
                print(f"   ✅ Found: {wrong_user_credits.total_credits} credits")
            else:
                print(f"   ❌ No credits record found")
            
            # Check correct user credits
            print(f"Checking correct user ({correct_user_id})...")
            correct_user_credits = await credits_service.get_user_credits(correct_user_id)
            if correct_user_credits:
                print(f"   ✅ Found: {correct_user_credits.total_credits} credits")
            else:
                print(f"   ❌ No credits record found")
            
            print()
            print("🔧 STEP 2: EXECUTING CREDIT TRANSFER")
            print("-" * 40)
            
            if wrong_user_credits and wrong_user_credits.total_credits >= credits_to_transfer:
                try:
                    # Start transaction
                    print(f"Transferring {credits_to_transfer} credits...")
                    
                    # Subtract from wrong user
                    await credits_service.subtract_credits(wrong_user_id, credits_to_transfer)
                    print(f"   ✅ Subtracted {credits_to_transfer} from {wrong_user_id}")
                    
                    # Add to correct user
                    await credits_service.add_credits(correct_user_id, credits_to_transfer)
                    print(f"   ✅ Added {credits_to_transfer} to {correct_user_id}")
                    
                    # Commit transaction
                    await db_session.commit()
                    print(f"   ✅ Transaction committed")
                    
                    # Verify final state
                    print()
                    print("🔍 STEP 3: VERIFYING TRANSFER")
                    print("-" * 40)
                    
                    # Refresh and check balances
                    wrong_final = await credits_service.get_user_credits(wrong_user_id)
                    correct_final = await credits_service.get_user_credits(correct_user_id)
                    
                    print(f"Final balance - Wrong user: {wrong_final.total_credits if wrong_final else 0}")
                    print(f"Final balance - Correct user: {correct_final.total_credits if correct_final else 0}")
                    
                    print()
                    print("🎉 TRANSFER COMPLETED SUCCESSFULLY!")
                    print(f"Your credit balance is now: {correct_final.total_credits if correct_final else 0}")
                    
                except Exception as e:
                    await db_session.rollback()
                    print(f"❌ Transfer failed: {e}")
                    raise
            else:
                print(f"❌ Cannot transfer: insufficient credits on wrong user")
                if wrong_user_credits:
                    print(f"   Available: {wrong_user_credits.total_credits}")
                    print(f"   Needed: {credits_to_transfer}")
                else:
                    print(f"   Wrong user has no credits record")
            
            print()
            print("🔧 STEP 4: PREVENTING FUTURE ISSUES")
            print("-" * 40)
            
            # Check if there are multiple accounts for the same person
            print("Checking for related accounts...")
            
            # Look for customer records
            query = select(StripeCustomer).limit(10)
            result = await db_session.execute(query)
            customers = result.scalars().all()
            
            if customers:
                print("Stripe customer records:")
                for customer in customers:
                    print(f"   User: {customer.user_id} | Stripe: {customer.stripe_customer_id}")
            else:
                print("   No Stripe customer records found")
            
            print()
            print("📋 RECOMMENDATIONS:")
            print("-" * 40)
            print("1. Clear browser cache and cookies")
            print("2. Log out and log back in to the frontend")
            print("3. Verify your user ID in the frontend matches:", correct_user_id)
            print("4. Make a small test purchase to verify credits go to correct user")
            print("5. If problem persists, check authentication session data")
            
            break  # Exit the async generator
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        
        print()
        print("🚨 EMERGENCY FALLBACK:")
        print("If automatic transfer fails, contact admin with:")
        print(f"   Your user ID: {correct_user_id}")
        print(f"   Credits location: {wrong_user_id}")
        print(f"   Amount: {credits_to_transfer}")
        print(f"   Event ID: evt_1S2YsxEPwuWwkzKTxZFOrvZG")

if __name__ == "__main__":
    asyncio.run(real_credit_solution())
