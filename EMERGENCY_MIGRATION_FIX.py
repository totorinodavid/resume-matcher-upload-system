#!/usr/bin/env python3
"""
EMERGENCY: Fix missing credits_balance column in production
This script will add the missing column that the migration failed to create
"""

import asyncio
import asyncpg
import os
from urllib.parse import urlparse

async def emergency_migration_fix():
    print("🚨 EMERGENCY MIGRATION FIX")
    print("==========================")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Try common locations
        env_files = ['.env', 'apps/backend/.env']
        for env_file in env_files:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('DATABASE_URL='):
                            database_url = line.split('=', 1)[1].strip().strip('"\'')
                            break
                if database_url:
                    break
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    print(f"🔗 Connecting to database...")
    
    try:
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Connect to database
        conn = await asyncpg.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/')
        )
        
        print("✅ Connected to database")
        
        # Check if credits_balance column exists
        check_column = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'credits_balance'
        """
        
        result = await conn.fetch(check_column)
        
        if result:
            print("✅ credits_balance column already exists")
            return True
        
        print("🔧 Adding missing credits_balance column...")
        
        # Add the missing column
        add_column_sql = """
        ALTER TABLE users 
        ADD COLUMN credits_balance INTEGER DEFAULT 0
        """
        
        await conn.execute(add_column_sql)
        print("✅ Successfully added credits_balance column")
        
        # Verify the column was added
        verify_result = await conn.fetch(check_column)
        
        if verify_result:
            print("✅ Column verified - migration fix complete")
            
            # Update alembic version table to mark migration as complete
            try:
                update_alembic = """
                INSERT INTO alembic_version (version_num) 
                VALUES ('0006_production_credits') 
                ON CONFLICT (version_num) DO NOTHING
                """
                await conn.execute(update_alembic)
                print("✅ Updated alembic version table")
            except Exception as e:
                print(f"⚠️ Could not update alembic table: {e}")
            
            return True
        else:
            print("❌ Column verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    finally:
        if 'conn' in locals():
            await conn.close()
            print("🔗 Database connection closed")

if __name__ == "__main__":
    success = asyncio.run(emergency_migration_fix())
    if success:
        print("\n🎉 EMERGENCY MIGRATION FIX COMPLETE!")
        print("🔄 Credits system should now work correctly")
    else:
        print("\n❌ Emergency migration fix failed")
