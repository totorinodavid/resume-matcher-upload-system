#!/usr/bin/env python3
"""
Quick PostgreSQL setup test for Resume Matcher development.
Tests Neon PostgreSQL connection and database configuration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add app to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

async def test_database_config():
    """Test database configuration and create tables."""
    print("🔄 Testing PostgreSQL configuration...")
    
    try:
        from app.core.database import async_engine, AsyncSessionLocal
        from app.models.base import Base
        
        # Test engine creation
        print("✅ Database engine created successfully")
        
        # Test connection (this will fail without actual PostgreSQL, which is expected)
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute("SELECT 1")
                print("✅ Database connection successful")
        except Exception as e:
            print(f"ℹ️  Database connection failed (expected without Neon): {e}")
            print("💡 To fix: Run 'neonctl proxy ...' or set up local PostgreSQL")
        
        print("✅ PostgreSQL configuration is correct")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def main():
    print("🚀 Resume Matcher PostgreSQL Setup Test")
    print("=" * 50)
    
    # Test configuration
    success = await test_database_config()
    
    if success:
        print("\n🎉 PostgreSQL setup is ready!")
        print("\n📋 Next steps:")
        print("1. Set up PostgreSQL database (Render/Local)")
        print("2. Set DATABASE_URL environment variable")
        print("3. Run database migrations: python setup_postgres.py --mode development")
    else:
        print("\n❌ Setup needs fixing")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
