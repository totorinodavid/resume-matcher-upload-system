#!/usr/bin/env python3
"""
🔍 CURRENT CREDIT SYSTEM ANALYSIS

Vollständige Analyse des aktuellen Credit-Systems im Resume Matcher.
"""

import asyncio
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def analyze_credit_system():
    """Analysiere das aktuelle Credit-System."""
    try:
        # Add backend to Python path
        backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
        if os.path.exists(backend_path):
            sys.path.insert(0, backend_path)
        
        from app.core.database import get_async_session_local
        from sqlalchemy import text
        
        logger.info("🔍 Analysiere das Resume Matcher Credit-System...")
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            
            print("\n" + "="*80)
            print("📊 CREDIT SYSTEM ARCHITECTURE ANALYSIS")
            print("="*80)
            
            # 1. Check User Model
            print("\n1️⃣  USER MODEL:")
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name='users'
                ORDER BY ordinal_position
            """))
            
            user_columns = result.fetchall()
            for col in user_columns:
                print(f"   - {col.column_name:<20} {col.data_type:<20} nullable:{col.is_nullable} default:{col.column_default}")
            
            # Check if users have credits_balance
            has_credits_balance = any(col.column_name == 'credits_balance' for col in user_columns)
            print(f"\n   ✅ credits_balance column exists: {has_credits_balance}")
            
            # 2. Check Credit Tables
            print("\n2️⃣  CREDIT TABLES:")
            
            # Check credit_ledger (legacy)
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM credit_ledger"))
                ledger_count = result.scalar()
                print(f"   📚 credit_ledger: {ledger_count} entries (legacy table)")
            except Exception as e:
                print(f"   ❌ credit_ledger: Table not found ({e})")
            
            # Check credit_transactions (new)
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM credit_transactions"))
                transactions_count = result.scalar()
                print(f"   💳 credit_transactions: {transactions_count} entries (new table)")
            except Exception as e:
                print(f"   ❌ credit_transactions: Table not found ({e})")
            
            # Check payments table
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM payments"))
                payments_count = result.scalar()
                print(f"   💰 payments: {payments_count} entries")
                
                # Show payment statuses
                result = await session.execute(text("""
                    SELECT status, COUNT(*) 
                    FROM payments 
                    GROUP BY status 
                    ORDER BY COUNT(*) DESC
                """))
                statuses = result.fetchall()
                if statuses:
                    print("   Payment statuses:")
                    for status, count in statuses:
                        print(f"     - {status}: {count}")
                        
            except Exception as e:
                print(f"   ❌ payments: Table not found ({e})")
            
            # Check stripe_customers
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM stripe_customers"))
                customers_count = result.scalar()
                print(f"   🏪 stripe_customers: {customers_count} entries")
            except Exception as e:
                print(f"   ❌ stripe_customers: Table not found ({e})")
            
            # 3. Check User Credit Balances
            print("\n3️⃣  USER CREDIT BALANCES:")
            
            # Count users
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            total_users = result.scalar()
            print(f"   👥 Total users: {total_users}")
            
            if has_credits_balance:
                # Show credit distribution
                result = await session.execute(text("""
                    SELECT 
                        credits_balance,
                        COUNT(*) as user_count
                    FROM users 
                    GROUP BY credits_balance 
                    ORDER BY credits_balance DESC
                    LIMIT 10
                """))
                balances = result.fetchall()
                print("   Credit balance distribution:")
                for balance, count in balances:
                    print(f"     - {balance} credits: {count} users")
                
                # Total credits in system
                result = await session.execute(text("SELECT SUM(credits_balance) FROM users"))
                total_credits = result.scalar() or 0
                print(f"   💎 Total credits in system: {total_credits}")
            
            # 4. Check Credit Services
            print("\n4️⃣  CREDIT SERVICES:")
            
            try:
                from app.services.credits_service import CreditsService
                credits_service = CreditsService(session)
                print("   ✅ CreditsService: Available")
                
                # Test balance for first user
                if total_users > 0:
                    result = await session.execute(text("SELECT id FROM users LIMIT 1"))
                    first_user_id = result.scalar()
                    if first_user_id:
                        balance = await credits_service.get_balance(user_id=str(first_user_id))
                        print(f"   📊 Test balance (user {first_user_id}): {balance} credits")
                        
            except Exception as e:
                print(f"   ❌ CreditsService: {e}")
            
            # 5. Check Webhook Processing
            print("\n5️⃣  WEBHOOK PROCESSING:")
            
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM processed_events"))
                events_count = result.scalar()
                print(f"   📨 processed_events: {events_count} webhook events")
                
                if events_count > 0:
                    result = await session.execute(text("""
                        SELECT provider, COUNT(*) 
                        FROM processed_events 
                        GROUP BY provider
                    """))
                    providers = result.fetchall()
                    for provider, count in providers:
                        print(f"     - {provider}: {count} events")
                        
            except Exception as e:
                print(f"   ❌ processed_events: Table not found ({e})")
            
            # 6. Check Stripe Events Table (from hotfix)
            print("\n6️⃣  STRIPE EVENTS (HOTFIX):")
            
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM stripe_events"))
                stripe_events_count = result.scalar()
                print(f"   ⚡ stripe_events: {stripe_events_count} events (hotfix table)")
                
                if stripe_events_count > 0:
                    result = await session.execute(text("""
                        SELECT event_type, processing_status, COUNT(*) 
                        FROM stripe_events 
                        GROUP BY event_type, processing_status
                    """))
                    events = result.fetchall()
                    for event_type, status, count in events:
                        print(f"     - {event_type} ({status}): {count}")
                        
            except Exception as e:
                print(f"   ❌ stripe_events: Table not found ({e})")
            
            # 7. Analyze Recent Activity
            print("\n7️⃣  RECENT ACTIVITY:")
            
            # Recent payments
            try:
                result = await session.execute(text("""
                    SELECT 
                        user_id,
                        amount_total_cents,
                        expected_credits,
                        status,
                        created_at
                    FROM payments 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """))
                recent_payments = result.fetchall()
                if recent_payments:
                    print("   Recent payments:")
                    for payment in recent_payments:
                        print(f"     - User {payment.user_id}: €{payment.amount_total_cents/100:.2f} → {payment.expected_credits} credits ({payment.status})")
                else:
                    print("   No recent payments found")
            except:
                pass
            
            # Recent credit transactions
            try:
                result = await session.execute(text("""
                    SELECT 
                        user_id,
                        delta_credits,
                        reason,
                        created_at
                    FROM credit_transactions 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """))
                recent_transactions = result.fetchall()
                if recent_transactions:
                    print("   Recent credit transactions:")
                    for tx in recent_transactions:
                        print(f"     - User {tx.user_id}: {tx.delta_credits:+} credits ({tx.reason})")
                else:
                    print("   No recent credit transactions found")
            except:
                pass
            
            print("\n" + "="*80)
            print("📋 SYSTEM ARCHITECTURE SUMMARY")
            print("="*80)
            
            # Architecture summary
            print(f"""
🏗️  CURRENT ARCHITECTURE:
   
   USER MODEL:
   - {total_users} users in system
   - credits_balance column: {'✅ EXISTS' if has_credits_balance else '❌ MISSING'}
   
   CREDIT STORAGE:
   - Legacy: credit_ledger table (backward compatibility)
   - Modern: credit_transactions + payments tables
   - Hotfix: stripe_events table for webhook deduplication
   
   PAYMENT FLOW:
   1. User purchases credits via Stripe
   2. Webhook processes checkout.session.completed
   3. Credits added to user account
   4. Payment status tracked through state machine
   
   SERVICES:
   - CreditsService: Manages credit balance and transactions
   - PaymentService: Handles payment processing
   - UltraEmergencyUserService: User resolution (recently fixed)
   - StripeProvider: Stripe integration
            """)
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the credit system analysis."""
    try:
        success = asyncio.run(analyze_credit_system())
        if success:
            print("\n✅ CREDIT SYSTEM ANALYSIS COMPLETE!")
        else:
            print("\n❌ Analysis failed - check logs above")
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 Analysis crashed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
