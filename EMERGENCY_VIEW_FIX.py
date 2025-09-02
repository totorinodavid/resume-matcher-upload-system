#!/usr/bin/env python3
"""
EMERGENCY DATABASE VIEW FIX
Creates missing v_credit_balance view that's causing production errors
"""

import psycopg2
import os
from urllib.parse import urlparse

def create_missing_view():
    """Create the missing v_credit_balance view"""
    
    # Use production database URL directly
    database_url = "postgresql://postgres:HrMZJqYRSZe0Tt7KY2xIfTOYCqrCKSdg@dpg-d2qkqqqdbo4c73c8ngeg-a.oregon-postgres.render.com/resume_matcher_db_e3f7"
    
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    # Parse the URL
    parsed = urlparse(database_url)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password,
            port=parsed.port or 5432,
            sslmode='require'
        )
        
        cursor = conn.cursor()
        
        print("🔗 Connected to database...")
        
        # Create the missing view
        create_view_sql = """
        CREATE OR REPLACE VIEW v_credit_balance AS
        SELECT 
            user_id,
            COALESCE(SUM(delta), 0) AS balance
        FROM credit_ledger
        GROUP BY user_id;
        """
        
        print("📝 Creating v_credit_balance view...")
        cursor.execute(create_view_sql)
        
        # Verify the view was created
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_name = 'v_credit_balance'
        """)
        
        result = cursor.fetchone()
        if result:
            print("✅ View v_credit_balance created successfully!")
            
            # Test the view
            cursor.execute("SELECT COUNT(*) FROM v_credit_balance")
            count = cursor.fetchone()[0]
            print(f"📊 View contains {count} user credit balances")
            
        else:
            print("❌ Failed to create view")
            return False
            
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 DATABASE VIEW FIX COMPLETE!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚨 EMERGENCY DATABASE VIEW FIX")
    print("=" * 50)
    
    success = create_missing_view()
    
    if success:
        print("\n🎯 CREDITS SYSTEM SHOULD NOW WORK!")
        print("✅ v_credit_balance view created")
        print("✅ Database error resolved")
    else:
        print("\n❌ FIX FAILED - CHECK DATABASE CONNECTION")
