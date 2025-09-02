#!/bin/bash
set -e

echo "🚀 NUCLEAR STARTUP INITIATED"
echo "Timestamp: $(date)"

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python -c "
import asyncio
import asyncpg
import os
import time

async def wait_for_db():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print('❌ DATABASE_URL not found')
        exit(1)
    
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = await asyncpg.connect(db_url)
            await conn.execute('SELECT 1')
            await conn.close()
            print('✅ Database connection successful')
            break
        except Exception as e:
            print(f'Database connection attempt {i+1}/{max_retries} failed: {e}')
            if i == max_retries - 1:
                print('❌ Database connection failed after max retries')
                exit(1)
            time.sleep(2)

asyncio.run(wait_for_db())
"

# NUCLEAR APPROACH: Direct database column creation
echo "🔥 NUCLEAR DATABASE OPERATION: Direct column creation"
python -c "
import asyncio
import asyncpg
import os

async def nuclear_db_fix():
    db_url = os.getenv('DATABASE_URL')
    conn = await asyncpg.connect(db_url)
    
    try:
        # Check if credits_balance column exists
        result = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'credits_balance'
        """)
        
        if not result:
            print('🔥 NUCLEAR: Adding credits_balance column directly')
            await conn.execute("""
                ALTER TABLE users ADD COLUMN credits_balance INTEGER DEFAULT 50;
            """)
            print('✅ credits_balance column created successfully')
        else:
            print('✅ credits_balance column already exists')
            
        # Verify column exists
        verification = await conn.fetch("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'credits_balance'
        """)
        print(f'✅ Column verification: {verification}')
        
    except Exception as e:
        print(f'❌ Nuclear database operation failed: {e}')
        # Continue anyway - don't fail startup
    finally:
        await conn.close()

asyncio.run(nuclear_db_fix())
"

# Run standard Alembic migrations as backup
echo "🔄 Running standard Alembic migrations (fallback)"
alembic upgrade head || echo "⚠️ Alembic migration warning (proceeding anyway)"

# Start the application
echo "🚀 Starting FastAPI application"
exec uvicorn main:app --host 0.0.0.0 --port 8000
