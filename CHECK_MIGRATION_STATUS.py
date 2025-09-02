#!/usr/bin/env python3
"""
EMERGENCY: Check if migration was executed on Render
"""
import asyncio
import asyncpg
import os
from datetime import datetime

async def check_migration_status():
    """Check if the credits_balance migration was applied"""
    
    # Database connection string from Render environment
    database_url = "postgresql://resume_user:5ExlTgw4c9WZ9lrJhJk9pJYyFGNZqBKE@dpg-d2qkqqqdbo4c73c8ngeg-a.oregon-postgres.render.com/resume_matcher_db_e3f7"
    
    try:
        print("🔍 Connecting to production database...")
        conn = await asyncpg.connect(database_url, ssl='require')
        
        # Check alembic version table
        print("\n📋 Checking applied migrations...")
        version_result = await conn.fetch("SELECT version_num FROM alembic_version ORDER BY version_num")
        print(f"Applied migrations: {[row['version_num'] for row in version_result]}")
        
        # Check if users table has credits_balance column
        print("\n🏗️  Checking users table structure...")
        table_info = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """)
        
        print("Users table columns:")
        has_credits_balance = False
        for col in table_info:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']}, default: {col['column_default']})")
            if col['column_name'] == 'credits_balance':
                has_credits_balance = True
        
        # Show specific migration we're looking for
        target_migration = "0009_add_users_credits_balance"
        migration_applied = any(target_migration in v['version_num'] for v in version_result)
        
        print(f"\n🎯 Target migration '{target_migration}' applied: {migration_applied}")
        print(f"🎯 credits_balance column exists: {has_credits_balance}")
        
        if not has_credits_balance:
            print("\n❌ PROBLEM: credits_balance column missing!")
            print("💡 SOLUTION: Need to manually apply the migration")
            
            # Try to apply the migration manually
            print("\n🚨 ATTEMPTING MANUAL MIGRATION...")
            try:
                await conn.execute("""
                    ALTER TABLE users 
                    ADD COLUMN credits_balance INTEGER NOT NULL DEFAULT 0
                """)
                print("✅ Manual migration executed successfully!")
                
                # Update alembic version table
                await conn.execute("""
                    UPDATE alembic_version 
                    SET version_num = '0009_add_users_credits_balance'
                """)
                print("✅ Alembic version updated!")
                
            except Exception as e:
                print(f"❌ Manual migration failed: {e}")
        else:
            print("\n✅ credits_balance column exists - migration was successful!")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print(f"🚨 EMERGENCY MIGRATION CHECK - {datetime.now()}")
    print("=" * 60)
    
    asyncio.run(check_migration_status())
