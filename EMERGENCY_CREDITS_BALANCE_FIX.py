#!/usr/bin/env python3
"""
EMERGENCY: Add missing credits_balance column to users table
CRITICAL: The backend expects users.credits_balance but it doesn't exist in production DB

ERROR: column users.credits_balance does not exist at character 43
SOLUTION: Add the column with default value 0
"""

import os
import asyncio
import psycopg2
from urllib.parse import urlparse
import sys

def get_database_url():
    """Get database URL from environment or Render"""
    # Try direct DATABASE_URL first
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # Try Render internal URL
    render_url = os.getenv("DATABASE_INTERNAL_URL") 
    if render_url:
        return render_url
        
    # Construct from components
    host = os.getenv("POSTGRES_HOST", "dpg-d2qkqqqdbo4c73c8ngeg-a.frankfurt-postgres.render.com")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD")
    database = os.getenv("POSTGRES_DB", "resume_matcher_db_e3f7")
    
    if not password:
        print("❌ No database password found in environment")
        return None
        
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def connect_to_database():
    """Connect to PostgreSQL database"""
    db_url = get_database_url()
    if not db_url:
        print("❌ Could not determine database URL")
        return None
        
    try:
        # Parse URL and connect
        print(f"🔗 Connecting to database...")
        conn = psycopg2.connect(db_url)
        print("✅ Connected to database successfully")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def fix_credits_balance_column():
    """Add missing credits_balance column to users table"""
    print("🚨 EMERGENCY: Fixing missing credits_balance column")
    print()
    
    conn = connect_to_database()
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        
        # Check if column already exists
        print("🔍 Checking if credits_balance column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'credits_balance';
        """)
        
        result = cursor.fetchone()
        
        if result:
            print("✅ credits_balance column already exists")
            print("🔍 Checking current values...")
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE credits_balance IS NOT NULL;")
            count = cursor.fetchone()[0]
            print(f"📊 Found {count} users with credits_balance values")
            
        else:
            print("❌ credits_balance column MISSING - Adding it now...")
            
            # Add the column with default value
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN credits_balance INTEGER NOT NULL DEFAULT 0;
            """)
            
            print("✅ Added credits_balance column to users table")
            
            # Verify the addition
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name = 'credits_balance';
            """)
            
            column_info = cursor.fetchone()
            if column_info:
                print(f"✅ Column verified: {column_info}")
            else:
                print("❌ Column verification failed")
                return False
        
        # Test the fix by running the problematic query
        print("🧪 Testing the fix with actual query...")
        cursor.execute("""
            SELECT users.id, users.email, users.name, users.credits_balance 
            FROM users 
            LIMIT 3;
        """)
        
        users = cursor.fetchall()
        print("✅ Query successful! Sample users:")
        for user in users:
            print(f"   User {user[0]}: {user[1]} - Credits: {user[3]}")
        
        # Commit the changes
        conn.commit()
        print()
        print("🎉 EMERGENCY FIX COMPLETED SUCCESSFULLY!")
        print("✅ credits_balance column is now available")
        print("✅ Backend should work without errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency fix failed: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()
        print("🔐 Database connection closed")

def main():
    """Main execution"""
    print("=" * 60)
    print("🚨 EMERGENCY DATABASE FIX")
    print("Problem: column users.credits_balance does not exist")
    print("Solution: Add the missing column")
    print("=" * 60)
    print()
    
    success = fix_credits_balance_column()
    
    print()
    print("=" * 60)
    if success:
        print("✅ EMERGENCY FIX SUCCESSFUL")
        print("📝 The credits system should now work properly")
        print("📝 All users now have credits_balance = 0 by default")
    else:
        print("❌ EMERGENCY FIX FAILED")
        print("📝 Manual intervention required")
        
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
