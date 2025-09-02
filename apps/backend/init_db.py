#!/usr/bin/env python3
"""Initialize database with all tables"""

import asyncio
from app.core.database import get_async_engine
from app.models.base import Base

async def init_database():
    """Create all tables in the database"""
    engine = get_async_engine()
    
    print("Creating all database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully!")
    
    # Create alembic_version table and mark as current
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """))
        
        # Mark as being at the latest migration
        await conn.execute(text("""
            INSERT INTO alembic_version (version_num) 
            VALUES ('0006_production_credits')
            ON CONFLICT (version_num) DO NOTHING
        """))
    
    print("Alembic version table created and marked as current!")

if __name__ == "__main__":
    from sqlalchemy import text
    asyncio.run(init_database())
