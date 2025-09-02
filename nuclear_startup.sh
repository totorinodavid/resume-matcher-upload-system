#!/bin/bash
set -e

echo "🔥 NUCLEAR STARTUP - DIRECT DATABASE FIX"
echo "========================================"

# Direct database column creation (bypassing Alembic)
echo "🔧 DIRECT DATABASE COLUMN CREATION..."
python3 -c "
import asyncio
import asyncpg
import os
import sys

async def direct_column_creation():
    try:
        print('Connecting to database...')
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        
        # Check if column exists
        result = await conn.fetch(
            'SELECT column_name FROM information_schema.columns WHERE table_name = \'users\' AND column_name = \'credits_balance\';'
        )
        
        if not result:
            print('🔧 Creating credits_balance column directly...')
            await conn.execute('ALTER TABLE users ADD COLUMN credits_balance INTEGER NOT NULL DEFAULT 0;')
            print('✅ credits_balance column created!')
        else:
            print('✅ credits_balance column already exists!')
        
        # Verify column exists
        result = await conn.fetch(
            'SELECT column_name FROM information_schema.columns WHERE table_name = \'users\' AND column_name = \'credits_balance\';'
        )
        
        if result:
            print('✅ VERIFICATION: credits_balance column confirmed!')
            
            # Test a simple select to ensure it works
            test_result = await conn.fetch('SELECT COUNT(*) as count FROM users LIMIT 1;')
            print(f'✅ TEST QUERY SUCCESS: Found {test_result[0]["count"]} users')
            
        await conn.close()
        return True
        
    except Exception as e:
        print(f'❌ Direct database fix failed: {e}')
        return False

success = asyncio.run(direct_column_creation())
sys.exit(0 if success else 1)
"

if [ $? -eq 0 ]; then
    echo "✅ DIRECT DATABASE FIX SUCCESSFUL!"
else
    echo "❌ DIRECT DATABASE FIX FAILED!"
    exit 1
fi

# Run migration anyway as backup
echo "🔄 Running Alembic migration as backup..."
alembic upgrade head || echo "Alembic failed but continuing..."

echo "🚀 Starting FastAPI application..."
exec fastapi run app/main.py --host 0.0.0.0 --port ${PORT:-8000}
