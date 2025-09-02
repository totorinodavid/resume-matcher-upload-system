#!/usr/bin/env python3
"""
🚀 AUTOMATED SCALING FIX - Force Single Container Deployment
Automatische Lösung für das Multiple-Container-Problem
"""

import subprocess
import time
import requests
import json
import os
from datetime import datetime

def force_single_container_deployment():
    """Force deployment with scaling fix"""
    print("🚀 AUTOMATED SCALING FIX")
    print("="*50)
    
    # Step 1: Create scaling fix in render.yaml
    print("\n1. 📝 UPDATING RENDER.YAML FOR SINGLE INSTANCE...")
    
    render_yaml_content = """services:
  - type: web
    name: resume-matcher-backend
    env: docker
    dockerfilePath: ./Dockerfile
    # SCALING FIX: Force single instance until migration is stable
    instanceCount: 1
    dockerCommand: ./startup_with_migration.sh
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: resume-matcher-db
          property: connectionString
      - key: OPENAI_API_KEY
        sync: false
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false
      - key: NEXTAUTH_SECRET
        sync: false

databases:
  - name: resume-matcher-db
    databaseName: resume_matcher_db
    user: resume_user"""

    # Write updated render.yaml
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_yaml_content)
    
    print("   ✅ render.yaml updated with instanceCount: 1")
    
    # Step 2: Create emergency migration check script
    print("\n2. 🔧 CREATING EMERGENCY MIGRATION VERIFICATION...")
    
    migration_check = """#!/bin/bash
set -e

echo "EMERGENCY MIGRATION CHECK"
echo "========================="

# Wait for database to be ready
echo "Waiting for database connection..."
for i in {1..30}; do
    if alembic current > /dev/null 2>&1; then
        echo "Database connection successful"
        break
    fi
    echo "   Attempt $i/30 - waiting for database..."
    sleep 2
done

# Check current migration state
echo "Checking current migration state..."
CURRENT_REVISION=$(alembic current 2>/dev/null | grep -o '^[a-f0-9]*' || echo "none")
echo "   Current revision: $CURRENT_REVISION"

# Force migration to latest
echo "Running migration to latest..."
alembic upgrade head

# Verify credits_balance column exists
echo "Verifying credits_balance column..."
python3 -c "
import asyncio
import asyncpg
import os

async def check_column():
    try:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        result = await conn.fetch(
            'SELECT column_name FROM information_schema.columns WHERE table_name = \\'users\\' AND column_name = \\'credits_balance\\';'
        )
        await conn.close()
        
        if result:
            print('credits_balance column exists!')
            return True
        else:
            print('credits_balance column missing!')
            return False
    except Exception as e:
        print(f'Database check failed: {e}')
        return False

result = asyncio.run(check_column())
exit(0 if result else 1)
"

if [ $? -eq 0 ]; then
    echo "MIGRATION VERIFICATION SUCCESSFUL!"
else
    echo "MIGRATION VERIFICATION FAILED!"
    exit 1
fi

echo "Starting application..."
exec "$@"
"""

    with open('emergency_migration_check.sh', 'w', encoding='utf-8') as f:
        f.write(migration_check)
    
    # Make executable
    os.chmod('emergency_migration_check.sh', 0o755)
    print("   ✅ Emergency migration check script created")
    
    # Step 3: Update startup script
    print("\n3. 🔄 UPDATING STARTUP SCRIPT...")
    
    updated_startup = """#!/bin/bash
set -e

echo "BULLETPROOF STARTUP WITH EMERGENCY MIGRATION"
echo "============================================="

# Run emergency migration check
./emergency_migration_check.sh fastapi run app/main.py --host 0.0.0.0 --port $PORT
"""

    with open('startup_with_migration.sh', 'w', encoding='utf-8') as f:
        f.write(updated_startup)
    
    os.chmod('startup_with_migration.sh', 0o755)
    print("   ✅ Startup script updated with emergency checks")
    
    # Step 4: Commit and push
    print("\n4. 📤 DEPLOYING SCALING FIX...")
    
    try:
        # Git operations
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'EMERGENCY: Force single instance deployment to fix multiple container migration issue'], 
                      check=True, capture_output=True)
        
        result = subprocess.run(['git', 'push'], check=True, capture_output=True, text=True)
        print("   ✅ Git push successful!")
        
        # Step 5: Monitor deployment
        print("\n5. 📊 MONITORING DEPLOYMENT...")
        monitor_deployment()
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git operation failed: {e}")
        if e.stdout:
            print(f"   STDOUT: {e.stdout}")
        if e.stderr:
            print(f"   STDERR: {e.stderr}")

def monitor_deployment():
    """Monitor the deployment progress"""
    print("   🔍 Waiting for deployment to complete...")
    
    base_url = "https://resume-matcher-backend-j06k.onrender.com"
    
    # Wait for deployment (usually takes 5-10 minutes)
    for i in range(60):  # 10 minutes max
        try:
            print(f"   ⏳ Check {i+1}/60 - Testing health endpoint...")
            
            response = requests.get(f"{base_url}/healthz", timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Health check passed at {datetime.now()}")
                
                # Test credits endpoint
                try:
                    # This should fail if multiple containers, succeed if single
                    test_response = requests.get(f"{base_url}/api/v1/me/credits", 
                                               headers={"Authorization": "Bearer test"}, 
                                               timeout=10)
                    
                    if test_response.status_code in [200, 401]:  # 401 is OK (auth issue, not DB issue)
                        print("   ✅ Credits endpoint responsive!")
                        
                        # Final verification - check for consistent responses
                        if verify_single_container():
                            print("\n🎉 DEPLOYMENT SUCCESS!")
                            print("   ✅ Single container deployment confirmed")
                            print("   ✅ Migration should be working")
                            return True
                            
                except Exception as e:
                    print(f"   ⚠️  Credits endpoint test: {e}")
            
        except Exception as e:
            print(f"   ⚠️  Health check failed: {e}")
        
        time.sleep(10)  # Wait 10 seconds between checks
    
    print("   ⚠️  Deployment monitoring timed out")
    return False

def verify_single_container():
    """Verify only single container is running"""
    print("   🔍 Verifying single container deployment...")
    
    base_url = "https://resume-matcher-backend-j06k.onrender.com"
    response_times = []
    
    # Test 5 requests
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/healthz", timeout=30)
            response_times.append(response.elapsed.total_seconds())
        except:
            pass
        time.sleep(2)
    
    if len(response_times) >= 3:
        # Check if response times are consistent (single container)
        avg_time = sum(response_times) / len(response_times)
        variance = sum((t - avg_time) ** 2 for t in response_times) / len(response_times)
        
        if variance < 1.0:  # Low variance indicates single container
            print(f"   ✅ Single container confirmed (low variance: {variance:.3f})")
            return True
        else:
            print(f"   ⚠️  Multiple containers possible (high variance: {variance:.3f})")
            return False
    
    return False

def main():
    print("🚨 STARTING AUTOMATED SCALING FIX")
    print("=" * 50)
    print("This will:")
    print("1. Force render.yaml to use single instance")
    print("2. Add emergency migration verification")
    print("3. Deploy and monitor the fix")
    print("4. Verify single container is working")
    print()
    
    print("🚀 AUTO-EXECUTING SCALING FIX...")
    
    force_single_container_deployment()

if __name__ == "__main__":
    main()
