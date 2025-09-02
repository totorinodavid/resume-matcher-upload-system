#!/usr/bin/env python3
"""
PostgreSQL-only setup script for Neon Local Connect.
Creates database, runs migrations, and seeds initial data.

Usage:
    python setup_postgres.py --mode development  # For local development
    python setup_postgres.py --mode production   # For production deployment
"""

import asyncio
import asyncpg
import argparse
import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from app.core.config import settings
from app.core.database import async_engine, AsyncSessionLocal
from app.models.base import Base


async def create_database_if_not_exists(connection_url: str, db_name: str) -> None:
    """Create database if it doesn't exist (PostgreSQL only)."""
    # Extract connection details without database name
    parts = connection_url.split("/")
    base_url = "/".join(parts[:-1])
    
    # Connect to postgres database to create our target database
    try:
        conn = await asyncpg.connect(f"{base_url}/postgres")
        
        # Check if database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not result:
            print(f"Creating database: {db_name}")
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database {db_name} created successfully")
        else:
            print(f"✅ Database {db_name} already exists")
            
        await conn.close()
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise


async def run_migrations() -> None:
    """Run Alembic migrations to create tables."""
    print("🔄 Running database migrations...")
    
    # Create all tables using SQLAlchemy metadata
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database migrations completed")


async def seed_initial_data() -> None:
    """Seed initial data for development."""
    print("🌱 Seeding initial data...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if we already have data
            from app.models.user import User
            result = await session.execute("SELECT COUNT(*) FROM users")
            user_count = result.scalar()
            
            if user_count > 0:
                print(f"✅ Database already has {user_count} users, skipping seed")
                return
            
            # Seed development users
            from app.models.user import User
            from sqlalchemy import text
            
            # Create test users with PostgreSQL-specific features
            seed_users = [
                {
                    "email": "admin@resumematcher.dev",
                    "name": "Admin User",
                    "metadata": {"role": "admin", "created_by": "seed_script"}
                },
                {
                    "email": "user@resumematcher.dev", 
                    "name": "Test User",
                    "metadata": {"role": "user", "created_by": "seed_script"}
                }
            ]
            
            for user_data in seed_users:
                # Use PostgreSQL JSONB for metadata
                query = text("""
                    INSERT INTO users (email, name, metadata, created_at, updated_at)
                    VALUES (:email, :name, :metadata::jsonb, NOW(), NOW()))
                    ON CONFLICT (email) DO NOTHING
                """)
                
                await session.execute(query, {
                    "email": user_data["email"],
                    "name": user_data["name"], 
                    "metadata": user_data["metadata"]
                })
            
            await session.commit()
            print("✅ Initial data seeded successfully")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


async def verify_setup() -> None:
    """Verify database setup and connectivity."""
    print("🔍 Verifying database setup...")
    
    try:
        async with AsyncSessionLocal() as session:
            # Test basic connectivity
            result = await session.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ Connected to: {version}")
            
            # Test table creation
            result = await session.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = result.scalar()
            print(f"✅ Found {table_count} tables in public schema")
            
            # Test PostgreSQL-specific features
            result = await session.execute("SELECT 1::jsonb")
            print("✅ JSONB support confirmed")
            
            # Test user data
            from app.models.user import User
            result = await session.execute("SELECT COUNT(*) FROM users")
            user_count = result.scalar()
            print(f"✅ Found {user_count} users in database")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        raise


async def main():
    parser = argparse.ArgumentParser(description="Setup PostgreSQL database for Resume Matcher")
    parser.add_argument(
        "--mode", 
        choices=["development", "production"],
        default="development",
        help="Setup mode"
    )
    parser.add_argument(
        "--skip-seed",
        action="store_true", 
        help="Skip seeding initial data"
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Setting up PostgreSQL database for {args.mode} mode")
    print(f"Database URL: {settings.ASYNC_DATABASE_URL.split('@')[1] if '@' in settings.ASYNC_DATABASE_URL else 'localhost'}")
    
    try:
        # Extract database name from URL
        db_name = settings.ASYNC_DATABASE_URL.split("/")[-1].split("?")[0]
        base_url = settings.ASYNC_DATABASE_URL.replace(f"postgresql+asyncpg://", "postgresql://")
        
        # Step 1: Create database if needed
        await create_database_if_not_exists(base_url, db_name)
        
        # Step 2: Run migrations
        await run_migrations()
        
        # Step 3: Seed data (development only)
        if args.mode == "development" and not args.skip_seed:
            await seed_initial_data()
        
        # Step 4: Verify setup
        await verify_setup()
        
        print(f"🎉 PostgreSQL setup completed successfully for {args.mode} mode!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
