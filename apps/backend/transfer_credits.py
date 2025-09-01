#!/usr/bin/env python3
"""
IMMEDIATE CREDIT TRANSFER SOLUTION
Transfer credits from wrong user to correct user
"""

import asyncio

async def transfer_credits():
    print("🔧 IMMEDIATE CREDIT TRANSFER")
    print("=" * 50)
    print()
    
    try:
        # Import backend components
        from app.core.database import get_db_session
        from app.services.credits_service import CreditsService
        
        # User IDs from the logs
        wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"
        correct_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
        credits_to_transfer = 50
        
        print(f"TRANSFERRING: {credits_to_transfer} credits")
        print(f"FROM: {wrong_user_id}")
        print(f"TO:   {correct_user_id}")
        print()
        
        async for db_session in get_db_session():
            credits_service = CreditsService(db_session)
            
            # Check current balances
            print("🔍 CHECKING CURRENT BALANCES...")
            wrong_balance = await credits_service.get_user_credits(wrong_user_id)
            correct_balance = await credits_service.get_user_credits(correct_user_id)
            
            print(f"Wrong user balance: {wrong_balance.total_credits if wrong_balance else 0}")
            print(f"Your current balance: {correct_balance.total_credits if correct_balance else 0}")
            print()
            
            if wrong_balance and wrong_balance.total_credits >= credits_to_transfer:
                print("✅ Transfer conditions met. Executing...")
                
                # Execute transfer
                await credits_service.subtract_credits(wrong_user_id, credits_to_transfer)
                print(f"   ✅ Subtracted {credits_to_transfer} from wrong user")
                
                await credits_service.add_credits(correct_user_id, credits_to_transfer)
                print(f"   ✅ Added {credits_to_transfer} to your account")
                
                await db_session.commit()
                print(f"   ✅ Transaction committed")
                
                # Verify final balances
                print()
                print("🎉 TRANSFER COMPLETED!")
                final_balance = await credits_service.get_user_credits(correct_user_id)
                print(f"Your new credit balance: {final_balance.total_credits if final_balance else 0}")
                
            else:
                print("❌ Transfer failed: insufficient credits on wrong user")
                if wrong_balance:
                    print(f"   Available: {wrong_balance.total_credits}")
                else:
                    print("   Wrong user not found")
            
            break
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(transfer_credits())
