#!/bin/bash
set -e

echo "EMERGENCY MIGRATION CHECK"
echo "========================="

# Wait for database to be ready
echo "Waiting for database connection..."
for i in {1..30}; do
    if alembic current > /dev/null 2>&1; then
        echo "Database connection successful"
        break
    fi
    echo "   Attempt $i/30 - waiting for database..."
    sleep 2
done

# Check current migration state
echo "Checking current migration state..."
CURRENT_REVISION=$(alembic current 2>/dev/null | grep -o '^[a-f0-9]*' || echo "none")
echo "   Current revision: $CURRENT_REVISION"

# Force migration to latest
echo "Running migration to latest..."
alembic upgrade head

# Verify credits_balance column exists
echo "Verifying credits_balance column..."
python3 -c "
import asyncio
import asyncpg
import os

async def check_column():
    try:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        result = await conn.fetch(
            'SELECT column_name FROM information_schema.columns WHERE table_name = \'users\' AND column_name = \'credits_balance\';'
        )
        await conn.close()
        
        if result:
            print('credits_balance column exists!')
            return True
        else:
            print('credits_balance column missing!')
            return False
    except Exception as e:
        print(f'Database check failed: {e}')
        return False

result = asyncio.run(check_column())
exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    echo "MIGRATION VERIFICATION SUCCESSFUL!"
else
    echo "MIGRATION VERIFICATION FAILED!"
    exit 1
fi

echo "Starting application..."
exec "$@"
