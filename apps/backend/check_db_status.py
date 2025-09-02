#!/usr/bin/env python3
"""Check database status and tables"""

import asyncio
from app.core.database import get_async_engine
from sqlalchemy import text

async def check_db_status():
    engine = get_async_engine()
    
    # Check alembic version
    async with engine.begin() as conn:
        try:
            result = await conn.execute(text('SELECT version_num FROM alembic_version'))
            version = result.scalar()
            print(f'Current alembic version: {version}')
        except Exception as e:
            print(f'No alembic_version table: {e}')
            
    # Check existing tables - each in its own transaction
    tables_to_check = [
        'users', 'credits', 'payments', 'credit_transactions', 'processed_events'
    ]
    
    for table in tables_to_check:
        async with engine.begin() as conn:
            try:
                result = await conn.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar()
                print(f'{table} table exists with {count} rows')
            except Exception as e:
                print(f'{table} table does not exist: {e}')
                
    # Check if credits_balance column exists in users table
    async with engine.begin() as conn:
        try:
            result = await conn.execute(text('SELECT column_name FROM information_schema.columns WHERE table_name = \'users\' AND column_name = \'credits_balance\''))
            if result.scalar():
                print('users.credits_balance column exists')
            else:
                print('users.credits_balance column does NOT exist')
        except Exception as e:
            print(f'Error checking users.credits_balance: {e}')

if __name__ == "__main__":
    asyncio.run(check_db_status())
