#!/usr/bin/env python3
"""
EMERGENCY DATABASE VIEW FIX - DIRECT CONNECTION
Uses the provided database URL to create missing v_credit_balance view
"""

import psycopg2
import sys

def create_missing_view():
    """Create the missing v_credit_balance view"""
    
    # Complete database URL (adding .oregon-postgres.render.com)
    database_url = "postgresql://resume_user:KNv2zOO0g2bZIqyB8zEeo4pYRlbBBBHY@dpg-d2qkqqqdbo4c73c8ngeg-a.oregon-postgres.render.com/resume_matcher_db_e3f7"
    
    try:
        print("🚨 EMERGENCY DATABASE VIEW FIX")
        print("=" * 50)
        print("🔗 Connecting to database...")
        
        # Connect to database
        conn = psycopg2.connect(database_url, sslmode='require')
        cursor = conn.cursor()
        
        print("✅ Connected successfully!")
        
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
            
            # Show sample data
            cursor.execute("SELECT user_id, balance FROM v_credit_balance LIMIT 3")
            sample_data = cursor.fetchall()
            print("🔍 Sample data:")
            for row in sample_data:
                print(f"   User: {row[0]}, Balance: {row[1]}")
            
        else:
            print("❌ Failed to create view")
            return False
            
        # Commit changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 DATABASE VIEW FIX COMPLETE!")
        print("✅ v_credit_balance view created")
        print("✅ Credits system should now work!")
        print("✅ ERROR 'relation does not exist' FIXED!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_missing_view()
    
    if success:
        print("\n🚀 CREDITS SYSTEM IS NOW FIXED!")
        sys.exit(0)
    else:
        print("\n❌ FIX FAILED")
        sys.exit(1)
