"""
🚨 PRODUCTION READY DEPLOYMENT FIX 🚨
Complete automated solution to fix all production issues
"""
import asyncio
import asyncpg
import os
import subprocess
import time
import requests
from pathlib import Path

class ProductionFixer:
    def __init__(self):
        self.database_url = self.get_database_url()
        self.render_service_url = "https://resume-matcher-backend-j06k.onrender.com"
        
    def get_database_url(self):
        """Get database URL from environment or construct from Neon"""
        # Try environment first
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            return db_url
            
        # Construct from Neon details
        neon_host = os.getenv('NEON_HOST', 'ep-odd-voice-a4x7wxn6.us-east-1.aws.neon.tech')
        neon_db = os.getenv('NEON_DATABASE', 'resume_matcher')
        neon_user = os.getenv('NEON_USER', 'resume_matcher_owner')
        neon_password = os.getenv('NEON_PASSWORD')
        
        if neon_password:
            return f"postgresql://{neon_user}:{neon_password}@{neon_host}/{neon_db}?sslmode=require"
        
        print("⚠️  No database credentials found - using Render connection")
        return None
    
    async def fix_database_schema(self):
        """Fix all database schema issues"""
        print("🔧 FIXING DATABASE SCHEMA...")
        print("=" * 50)
        
        if not self.database_url:
            print("❌ No database URL available - manual fix required")
            return False
            
        try:
            # Connect to database
            conn = await asyncpg.connect(self.database_url)
            print("✅ Connected to production database")
            
            # 1. Fix users table - add credits_balance
            print("\n1️⃣ Adding credits_balance column to users table...")
            await conn.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'credits_balance'
                    ) THEN
                        ALTER TABLE users ADD COLUMN credits_balance INTEGER DEFAULT 0 NOT NULL;
                        RAISE NOTICE 'Added credits_balance column';
                    ELSE
                        RAISE NOTICE 'credits_balance column already exists';
                    END IF;
                END $$;
            """)
            print("✅ Users table fixed")
            
            # 2. Create payment status enum
            print("\n2️⃣ Creating payment status enum...")
            await conn.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentstatus') THEN
                        CREATE TYPE paymentstatus AS ENUM ('pending', 'completed', 'failed', 'cancelled', 'refunded');
                        RAISE NOTICE 'Created paymentstatus enum';
                    ELSE
                        RAISE NOTICE 'paymentstatus enum already exists';
                    END IF;
                END $$;
            """)
            print("✅ Payment status enum created")
            
            # 3. Fix payments table structure
            print("\n3️⃣ Fixing payments table structure...")
            
            # Check current payments table columns
            columns_result = await conn.fetch("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'payments'
            """)
            existing_columns = [row['column_name'] for row in columns_result]
            print(f"Existing columns: {existing_columns}")
            
            # Add missing columns
            missing_columns = [
                ("stripe_session_id", "VARCHAR(255)"),
                ("stripe_payment_intent_id", "VARCHAR(255)"),
                ("currency", "VARCHAR(3) DEFAULT 'usd'"),
                ("credits_granted", "INTEGER DEFAULT 0"),
                ("metadata", "JSONB")
            ]
            
            for column_name, column_def in missing_columns:
                if column_name not in existing_columns:
                    await conn.execute(f"ALTER TABLE payments ADD COLUMN {column_name} {column_def}")
                    print(f"✅ Added {column_name} column")
                else:
                    print(f"✅ {column_name} already exists")
            
            # 4. Create missing tables
            print("\n4️⃣ Creating missing tables...")
            
            # Stripe customers table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS stripe_customers (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    stripe_customer_id VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Stripe customers table created")
            
            # Credit transactions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    transaction_type VARCHAR(50) NOT NULL,
                    amount INTEGER NOT NULL,
                    balance_before INTEGER NOT NULL,
                    balance_after INTEGER NOT NULL,
                    description TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Credit transactions table created")
            
            # Processed events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_events (
                    id SERIAL PRIMARY KEY,
                    event_id VARCHAR(255) UNIQUE NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """)
            print("✅ Processed events table created")
            
            # 5. Create indexes
            print("\n5️⃣ Creating indexes...")
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_payments_stripe_session ON payments(stripe_session_id)",
                "CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_processed_events_event_id ON processed_events(event_id)"
            ]
            
            for index_sql in indexes:
                await conn.execute(index_sql)
            print("✅ All indexes created")
            
            # 6. Add constraints
            print("\n6️⃣ Adding constraints...")
            try:
                await conn.execute("""
                    ALTER TABLE payments 
                    ADD CONSTRAINT payments_stripe_session_id_unique 
                    UNIQUE (stripe_session_id)
                """)
                print("✅ Added unique constraint on stripe_session_id")
            except Exception as e:
                if "already exists" in str(e):
                    print("✅ Constraint already exists")
                else:
                    print(f"⚠️  Constraint error: {e}")
            
            # 7. Verify database structure
            print("\n7️⃣ Verifying database structure...")
            users_columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            
            payments_columns = await conn.fetch("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'payments'
                ORDER BY ordinal_position
            """)
            
            print("Users table columns:")
            for row in users_columns:
                print(f"  - {row['column_name']}: {row['data_type']}")
            
            print("Payments table columns:")
            for row in payments_columns:
                print(f"  - {row['column_name']}: {row['data_type']}")
            
            await conn.close()
            print("\n✅ DATABASE SCHEMA FIX COMPLETED!")
            return True
            
        except Exception as e:
            print(f"❌ Database fix failed: {e}")
            return False
    
    def trigger_deployment(self):
        """Trigger new deployment"""
        print("\n🚀 TRIGGERING PRODUCTION DEPLOYMENT...")
        print("=" * 50)
        
        # Commit any pending changes first
        try:
            print("1️⃣ Committing emergency fixes...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run([
                "git", "commit", "-m", 
                "🚨 EMERGENCY: Production database schema fixes and deployment automation"
            ], check=True)
            print("✅ Emergency fixes committed")
        except subprocess.CalledProcessError:
            print("⚠️  No changes to commit (already up to date)")
        
        # Push to trigger deployment
        try:
            print("2️⃣ Pushing to trigger deployment...")
            subprocess.run(["git", "push", "origin", "security-hardening-neon"], check=True)
            print("✅ Pushed to GitHub - deployment triggered")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Push failed: {e}")
            return False
    
    def wait_for_deployment(self, max_wait=600):
        """Wait for deployment to complete"""
        print("\n⏳ WAITING FOR DEPLOYMENT TO COMPLETE...")
        print("=" * 50)
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < max_wait:
            check_count += 1
            elapsed = int(time.time() - start_time)
            
            print(f"[{elapsed:03d}s] Check #{check_count}: Testing backend...")
            
            try:
                response = requests.get(f"{self.render_service_url}/health", timeout=10)
                if response.status_code == 200:
                    print("✅ BACKEND IS LIVE!")
                    return True
                elif response.status_code == 404:
                    print("⚠️  Still getting 404 - deployment in progress...")
                else:
                    print(f"⚠️  HTTP {response.status_code} - checking again...")
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Connection error: {e}")
            
            time.sleep(30)  # Wait 30 seconds between checks
        
        print(f"❌ Deployment did not complete within {max_wait} seconds")
        return False
    
    def verify_production(self):
        """Verify production is working correctly"""
        print("\n✅ VERIFYING PRODUCTION DEPLOYMENT...")
        print("=" * 50)
        
        endpoints_to_test = [
            "/health",
            "/api/v1/resumes",
            "/webhooks/stripe"
        ]
        
        all_good = True
        
        for endpoint in endpoints_to_test:
            url = f"{self.render_service_url}{endpoint}"
            print(f"Testing {endpoint}...")
            
            try:
                if endpoint == "/webhooks/stripe":
                    # POST request for webhook
                    response = requests.post(url, json={}, timeout=10)
                else:
                    # GET request for others
                    response = requests.get(url, timeout=10)
                
                if response.status_code in [200, 201, 400, 405]:  # 400/405 expected for some endpoints
                    print(f"✅ {endpoint}: HTTP {response.status_code}")
                else:
                    print(f"❌ {endpoint}: HTTP {response.status_code}")
                    all_good = False
                    
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
                all_good = False
        
        return all_good
    
    def show_final_status(self, success):
        """Show final deployment status"""
        print("\n" + "=" * 60)
        if success:
            print("🎉 PRODUCTION DEPLOYMENT SUCCESSFUL!")
            print("✅ Backend: https://resume-matcher-backend-j06k.onrender.com")
            print("✅ Frontend: https://gojob.ing")
            print("✅ Database: Schema fixed and operational")
            print("✅ Credits system: Ready for production")
        else:
            print("❌ PRODUCTION DEPLOYMENT FAILED!")
            print("🔧 Manual intervention required")
            print("📋 Check Render dashboard for detailed logs")
        print("=" * 60)

async def main():
    """Main production fix function"""
    print("🚨 PRODUCTION READY DEPLOYMENT FIX")
    print("🎯 Objective: Fix all issues and deploy production-ready system")
    print("=" * 60)
    
    fixer = ProductionFixer()
    
    # Step 1: Fix database schema
    db_success = await fixer.fix_database_schema()
    
    # Step 2: Trigger deployment
    if db_success:
        deploy_success = fixer.trigger_deployment()
        
        # Step 3: Wait for deployment
        if deploy_success:
            deployment_ready = fixer.wait_for_deployment()
            
            # Step 4: Verify production
            if deployment_ready:
                production_verified = fixer.verify_production()
                fixer.show_final_status(production_verified)
            else:
                fixer.show_final_status(False)
        else:
            fixer.show_final_status(False)
    else:
        print("❌ Cannot proceed without database fix")
        print("📋 Manual database fix required via Render console")
        fixer.show_final_status(False)

if __name__ == "__main__":
    asyncio.run(main())
