"""
🚨 EMERGENCY RENDER DEPLOYMENT WITH DATABASE FIX 🚨
This script will:
1. Check Render deployment status
2. Apply database fixes
3. Trigger redeployment
"""
import os
import requests
import time
import json

def check_render_service():
    """Check Render service status"""
    service_id = "srv-ctcq6m08fa8c73dv01ng"  # Backend service ID
    
    print("🔍 Checking Render service status...")
    
    # Try to get service info
    try:
        response = requests.get(f"https://api.render.com/v1/services/{service_id}")
        if response.status_code == 200:
            service_data = response.json()
            print(f"✅ Service found: {service_data.get('name', 'Unknown')}")
            print(f"   Status: {service_data.get('serviceDetails', {}).get('buildCommand', 'Unknown')}")
            return True
        else:
            print(f"❌ Could not get service info: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking service: {e}")
        return False

def trigger_manual_deploy():
    """Trigger manual deployment"""
    service_id = "srv-ctcq6m08fa8c73dv01ng"
    
    print("🚀 Triggering manual deployment...")
    
    try:
        # This would need Render API key for actual deployment
        print("⚠️  Manual deployment trigger would require Render API key")
        print("   Please go to Render dashboard and trigger deployment manually")
        print("   URL: https://dashboard.render.com/web/srv-ctcq6m08fa8c73dv01ng")
        return True
    except Exception as e:
        print(f"❌ Error triggering deployment: {e}")
        return False

def check_database_connection():
    """Check if we can connect to production database"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ No DATABASE_URL found in environment")
        return False
    
    print("🔍 Checking database connection...")
    print(f"   Database: {database_url[:50]}...")
    
    # Try basic connection test
    try:
        import asyncpg
        import asyncio
        
        async def test_connection():
            try:
                conn = await asyncpg.connect(database_url)
                await conn.close()
                return True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
        
        result = asyncio.run(test_connection())
        if result:
            print("✅ Database connection successful")
        return result
        
    except ImportError:
        print("⚠️  asyncpg not available for connection test")
        return None
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main emergency deployment function"""
    print("🚨 EMERGENCY RENDER DEPLOYMENT WITH DATABASE FIX")
    print("=" * 60)
    
    # 1. Check service status
    service_ok = check_render_service()
    
    # 2. Check database
    db_ok = check_database_connection()
    
    # 3. Show emergency instructions
    print("\n📋 EMERGENCY DEPLOYMENT STEPS:")
    print("1. Go to Render Dashboard: https://dashboard.render.com/")
    print("2. Navigate to: Web Services > resume-matcher-backend")
    print("3. Click 'Manual Deploy' button")
    print("4. Select 'Clear build cache & deploy'")
    print("5. Monitor deployment logs for database migration")
    
    print("\n🗃️  DATABASE FIX OPTIONS:")
    print("1. Use Render Database Console:")
    print("   - Go to PostgreSQL Database in Render")
    print("   - Open 'Connect' tab")
    print("   - Use 'External Connection' or 'Shell'")
    print("   - Run the SQL script: EMERGENCY_DATABASE_FIX.sql")
    
    print("\n2. Direct SQL Commands to run:")
    print("   -- Add credits_balance column")
    print("   ALTER TABLE users ADD COLUMN IF NOT EXISTS credits_balance INTEGER DEFAULT 0 NOT NULL;")
    print("   -- Add missing payment columns")
    print("   ALTER TABLE payments ADD COLUMN IF NOT EXISTS stripe_session_id VARCHAR(255);")
    print("   ALTER TABLE payments ADD COLUMN IF NOT EXISTS stripe_payment_intent_id VARCHAR(255);")
    print("   ALTER TABLE payments ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'usd';")
    print("   ALTER TABLE payments ADD COLUMN IF NOT EXISTS credits_granted INTEGER DEFAULT 0;")
    print("   ALTER TABLE payments ADD COLUMN IF NOT EXISTS metadata JSONB;")
    
    print("\n🎯 IMMEDIATE ACTION REQUIRED:")
    print("1. Fix database schema using Render console")
    print("2. Trigger manual deployment")
    print("3. Monitor deployment logs")
    print("4. Test webhook endpoints")
    
    # 4. Try to trigger deployment
    trigger_manual_deploy()

if __name__ == "__main__":
    main()
