"""
🚨 EMERGENCY PAYMENTS TABLE FIX 🚨
Fix the payments table structure - add missing columns
"""
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def emergency_payments_fix():
    """Emergency fix for payments table missing columns"""
    
    print("🚨 EMERGENCY PAYMENTS TABLE FIX STARTING")
    print("=" * 50)
    
    # Database connection from environment
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://user:password@localhost:5432/resume_matcher')
    
    engine = create_async_engine(database_url, echo=True)
    
    async with engine.begin() as conn:
        # 1. Check current payments table structure
        print("\n1️⃣ Checking payments table structure...")
        payments_columns = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'payments'
            ORDER BY ordinal_position
        """))
        
        existing_columns = [row[0] for row in payments_columns.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # 2. Add missing columns
        missing_columns = [
            ("stripe_session_id", "VARCHAR(255)"),
            ("stripe_payment_intent_id", "VARCHAR(255)"),
            ("currency", "VARCHAR(3) DEFAULT 'usd'"),
            ("credits_granted", "INTEGER DEFAULT 0"),
            ("metadata", "JSONB"),
        ]
        
        for column_name, column_def in missing_columns:
            if column_name not in existing_columns:
                print(f"❌ Missing column: {column_name} - ADDING NOW")
                await conn.execute(text(f"ALTER TABLE payments ADD COLUMN {column_name} {column_def}"))
                print(f"✅ Added {column_name} column")
            else:
                print(f"✅ Column {column_name} already exists")
        
        # 3. Add unique constraint if missing
        print("\n2️⃣ Adding unique constraint on stripe_session_id...")
        try:
            await conn.execute(text("""
                ALTER TABLE payments 
                ADD CONSTRAINT payments_stripe_session_id_unique 
                UNIQUE (stripe_session_id)
            """))
            print("✅ Added unique constraint on stripe_session_id")
        except Exception as e:
            if "already exists" in str(e):
                print("✅ Unique constraint already exists")
            else:
                print(f"⚠️ Could not add constraint: {e}")
        
        # 4. Verify the fix
        print("\n3️⃣ Verifying payments table structure...")
        payments_columns = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'payments'
            ORDER BY ordinal_position
        """))
        
        print("Final payments table structure:")
        for row in payments_columns.fetchall():
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        print("\n✅ PAYMENTS TABLE FIX COMPLETED!")

if __name__ == "__main__":
    asyncio.run(emergency_payments_fix())
