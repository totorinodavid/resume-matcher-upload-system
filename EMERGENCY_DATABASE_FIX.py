#!/usr/bin/env python3
"""
🚨 EMERGENCY DATABASE FIX
Adds missing credits_balance column to production database
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Production database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql://resume_user:KNv2zOO0g2bZIqyB8zEeo4pYRlbBBBHY@dpg-d2qkqqqdbo4c73c8ngeg-a.frankfurt-postgres.render.com:5432/resume_matcher_db_e3f7"

# Convert to async URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def emergency_database_fix():
    """Add missing credits_balance column and create essential tables"""
    print("🚨 EMERGENCY DATABASE FIX STARTING")
    print("=" * 50)
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        
        # 1. Check if credits_balance column exists
        print("1️⃣ Checking credits_balance column...")
        check_column = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'credits_balance'
        """))
        
        column_exists = check_column.fetchone()
        
        if not column_exists:
            print("❌ credits_balance column missing - ADDING NOW")
            
            # Add credits_balance column
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN credits_balance INTEGER DEFAULT 0 NOT NULL
            """))
            
            print("✅ Added credits_balance column")
        else:
            print("✅ credits_balance column already exists")
        
        # 2. Create payment_status enum if not exists
        print("\n2️⃣ Creating payment_status enum...")
        await conn.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentstatus') THEN
                    CREATE TYPE paymentstatus AS ENUM ('pending', 'completed', 'failed', 'cancelled', 'refunded');
                END IF;
            END $$;
        """))
        
        # 3. Create essential credits tables
        print("3️⃣ Creating essential credits tables...")
        
        # Stripe customers table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stripe_customers (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                stripe_customer_id VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Payments table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                stripe_session_id VARCHAR(255) UNIQUE,
                stripe_payment_intent_id VARCHAR(255),
                amount_cents INTEGER NOT NULL,
                currency VARCHAR(3) DEFAULT 'usd',
                status paymentstatus DEFAULT 'pending',
                credits_granted INTEGER DEFAULT 0,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Credit transactions table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                transaction_type VARCHAR(50) NOT NULL,
                amount INTEGER NOT NULL,
                balance_before INTEGER NOT NULL,
                balance_after INTEGER NOT NULL,
                description TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Processed events table (for idempotency)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS processed_events (
                id SERIAL PRIMARY KEY,
                event_id VARCHAR(255) UNIQUE NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            );
        """))
        
        # Create indexes
        print("4️⃣ Creating indexes...")
        
        # Create indexes one by one to avoid multi-statement error
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_payments_stripe_session ON payments(stripe_session_id)",
            "CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_processed_events_event_id ON processed_events(event_id)"
        ]
        
        for index_sql in indexes:
            await conn.execute(text(index_sql))
        
        print("✅ Database fix completed successfully!")
        
        # 5. Verify the fix
        print("\n5️⃣ Verifying database structure...")
        
        # Check users table structure
        users_columns = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        
        print("📋 Users table columns:")
        for row in users_columns.fetchall():
            print(f"  - {row[0]}: {row[1]} {'NULL' if row[2] == 'YES' else 'NOT NULL'} {f'DEFAULT {row[3]}' if row[3] else ''}")
        
        # Check if tables exist
        tables_check = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('payments', 'credit_transactions', 'processed_events', 'stripe_customers')
            ORDER BY table_name
        """))
        
        print("\n📋 Credits tables created:")
        for row in tables_check.fetchall():
            print(f"  ✅ {row[0]}")
    
    await engine.dispose()
    
    print("\n🎉 EMERGENCY DATABASE FIX COMPLETE!")
    print("✅ credits_balance column added")
    print("✅ Essential credits tables created")
    print("✅ Indexes created for performance")
    print("✅ Database ready for credits processing")

if __name__ == "__main__":
    asyncio.run(emergency_database_fix())
