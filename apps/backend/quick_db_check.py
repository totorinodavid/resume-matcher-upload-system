#!/usr/bin/env python3
"""Quick database verification for hotfix"""

import asyncio
async def main():
    from app.core.database import get_async_session_local
    from sqlalchemy import text
    
    session_factory = get_async_session_local()
    async with session_factory() as session:
        # Check tables
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('stripe_events', 'users')
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        print(f"✅ Database tables found: {tables}")
        
        # Check credits_balance column
        result = await session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='credits_balance'
        """))
        credits_col = result.fetchone()
        print(f"✅ credits_balance column: {credits_col}")
        
        # Check stripe_events columns
        result = await session.execute(text("""
            SELECT COUNT(*) as column_count
            FROM information_schema.columns 
            WHERE table_name='stripe_events'
        """))
        stripe_cols = result.scalar()
        print(f"✅ stripe_events columns: {stripe_cols}")
        
        # Check current users
        result = await session.execute(text("""
            SELECT COUNT(*) as user_count, 
                   COALESCE(SUM(credits_balance), 0) as total_credits
            FROM users
        """))
        stats = result.fetchone()
        print(f"✅ User stats: {stats.user_count} users, {stats.total_credits} total credits")

if __name__ == "__main__":
    asyncio.run(main())
