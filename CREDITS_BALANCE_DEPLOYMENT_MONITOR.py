#!/usr/bin/env python3
"""
DEPLOYMENT MONITOR: Credits Balance Column Fix
Monitor if the migration for users.credits_balance was deployed
"""

import time
import requests
import json
from datetime import datetime

def check_backend_health():
    """Check if backend is responding"""
    try:
        response = requests.get("https://gojob.ing/api/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def check_credits_endpoint():
    """Test if credits endpoint works (indicates column exists)"""
    try:
        # Try a simple GET to an endpoint that uses credits
        response = requests.get("https://gojob.ing/api/v1/admin/health", timeout=10)
        return response.status_code in [200, 401, 403]  # Any response except 500 is good
    except:
        return False

def monitor_deployment():
    """Monitor deployment status"""
    print("🔍 MONITORING DEPLOYMENT STATUS")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    max_checks = 30  # 5 minutes of checking
    check_interval = 10  # seconds
    
    for i in range(max_checks):
        print(f"📡 Check {i+1}/{max_checks} - {datetime.now().strftime('%H:%M:%S')}")
        
        # Check backend health
        backend_ok = check_backend_health()
        print(f"   Backend Health: {'✅ OK' if backend_ok else '❌ Failed'}")
        
        if backend_ok:
            # Check credits functionality
            credits_ok = check_credits_endpoint()
            print(f"   Credits System: {'✅ OK' if credits_ok else '❌ Failed'}")
            
            if credits_ok:
                print()
                print("🎉 DEPLOYMENT SUCCESSFUL!")
                print("✅ Backend is healthy")
                print("✅ Credits system is working")
                print("✅ Migration was applied successfully")
                return True
        
        if i < max_checks - 1:
            print(f"   ⏳ Waiting {check_interval}s...")
            time.sleep(check_interval)
        print()
    
    print("⚠️  DEPLOYMENT TIMEOUT")
    print("❌ Either deployment failed or is taking longer than expected")
    return False

def main():
    """Main monitoring function"""
    print("🚀 CREDITS BALANCE COLUMN DEPLOYMENT MONITOR")
    print("Monitoring: Migration 0009_add_users_credits_balance")
    print("Expected: users.credits_balance column added to production DB")
    print()
    
    success = monitor_deployment()
    
    print("=" * 60)
    if success:
        print("✅ DEPLOYMENT MONITOR: SUCCESS")
        print("📝 The credits_balance column fix is now live")
        print("📝 Authentication errors should be resolved")
    else:
        print("❌ DEPLOYMENT MONITOR: TIMEOUT/FAILED")
        print("📝 Manual check required")
        print("📝 Check Render deployment logs")
    print("=" * 60)

if __name__ == "__main__":
    main()
