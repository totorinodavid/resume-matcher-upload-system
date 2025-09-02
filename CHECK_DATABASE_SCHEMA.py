#!/usr/bin/env python3
"""
CURRENT DATABASE SCHEMA CHECKER
Check what's actually in the production database
"""

import os
import psycopg2
from urllib.parse import urlparse

def connect_db():
    """Connect to production database"""
    # Try multiple connection methods
    
    # Method 1: Direct DATABASE_URL from environment
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            conn = psycopg2.connect(db_url)
            print("✅ Connected via DATABASE_URL")
            return conn
        except:
            pass
    
    # Method 2: Resume user with SSL
    try:
        db_url = "postgresql://resume_user:6UrnApQoBBq3zPPwjFZxEXrGJm0NKYjV@dpg-d2qkqqqdbo4c73c8ngeg-a.frankfurt-postgres.render.com:5432/resume_matcher_db_e3f7?sslmode=require"
        conn = psycopg2.connect(db_url)
        print("✅ Connected via resume_user with SSL")
        return conn
    except Exception as e:
        print(f"❌ resume_user connection failed: {e}")
    
    # Method 3: Postgres user with SSL
    try:
        db_url = "postgresql://postgres:6UrnApQoBBq3zPPwjFZxEXrGJm0NKYjV@dpg-d2qkqqqdbo4c73c8ngeg-a.frankfurt-postgres.render.com:5432/resume_matcher_db_e3f7?sslmode=require"
        conn = psycopg2.connect(db_url)
        print("✅ Connected via postgres with SSL")
        return conn
    except Exception as e:
        print(f"❌ postgres connection failed: {e}")
    
    print("❌ All connection methods failed")
    return None

def check_users_table():
    """Check the actual structure of users table"""
    print("🔍 CHECKING USERS TABLE STRUCTURE")
    print("=" * 50)
    
    conn = connect_db()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        # Get all columns in users table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("📊 USERS TABLE COLUMNS:")
        for col in columns:
            print(f"   {col[0]} | {col[1]} | nullable: {col[2]} | default: {col[3]}")
        
        print()
        
        # Check specifically for credits_balance
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name = 'credits_balance';
        """)
        
        result = cursor.fetchone()
        if result:
            print("✅ credits_balance column EXISTS")
        else:
            print("❌ credits_balance column MISSING")
        
        print()
        
        # Get sample data
        cursor.execute("SELECT id, email, name FROM users LIMIT 3;")
        users = cursor.fetchall()
        print("👥 SAMPLE USERS:")
        for user in users:
            print(f"   {user[0]} | {user[1]} | {user[2]}")
            
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
    finally:
        cursor.close()
        conn.close()

def check_migration_status():
    """Check which migrations have been applied"""
    print("\n🔍 CHECKING MIGRATION STATUS")
    print("=" * 50)
    
    conn = connect_db()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        # Check if alembic_version table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            );
        """)
        
        if cursor.fetchone()[0]:
            cursor.execute("SELECT version_num FROM alembic_version;")
            version = cursor.fetchone()
            if version:
                print(f"📝 Current migration version: {version[0]}")
            else:
                print("📝 No migration version recorded")
        else:
            print("❌ No alembic_version table found")
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Main function"""
    print("🔍 PRODUCTION DATABASE SCHEMA ANALYSIS")
    print("Checking what's actually in the database...")
    print()
    
    check_users_table()
    check_migration_status()
    
    print("\n" + "=" * 50)
    print("Analysis complete!")

if __name__ == "__main__":
    main()
