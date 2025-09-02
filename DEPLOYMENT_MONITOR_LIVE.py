#!/usr/bin/env python3
"""
Monitor Render deployment and migration execution
"""
import time
import requests
from datetime import datetime

def test_credits_endpoint():
    """Test if credits endpoint works (indicates migration success)"""
    try:
        # Test with a sample token
        headers = {
            'Authorization': 'Bearer gojob_eyJzdWIiOiI1ODk3NWY2ZC1lYzQ4LTQ4MWYtODk2Yi1jYzQ1ZTMzY2M5OWIiLCJlbWFpbCI6ImRhdmlzLnRoZXJhQGdtYWlsLmNvbSIsIm5hbWUiOiJkYXZpcyB0In0'
        }
        
        response = requests.get(
            'https://resume-matcher-backend-j06k.onrender.com/api/v1/me/credits',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Credits endpoint working! Response: {data}")
            return True
        else:
            print(f"❌ Credits endpoint failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Credits endpoint test failed: {e}")
        return False

def monitor_deployment():
    """Monitor the deployment and test for migration success"""
    
    print(f"🚨 DEPLOYMENT MONITOR - {datetime.now()}")
    print("=" * 60)
    print("🔍 Monitoring deployment status...")
    print("⏱️  Waiting for deployment to complete...")
    
    # Wait a bit for deployment to start
    time.sleep(30)
    
    for attempt in range(1, 11):  # Monitor for 10 attempts
        print(f"\n📊 Check #{attempt} - {datetime.now().strftime('%H:%M:%S')}")
        
        # Test if the application is responding
        try:
            response = requests.get(
                'https://resume-matcher-backend-j06k.onrender.com/healthz',
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Application is responding")
                
                # Test credits endpoint to see if migration worked
                if test_credits_endpoint():
                    print("🎉 MIGRATION SUCCESS! credits_balance column is working!")
                    return True
                else:
                    print("⚠️  Application responding but credits endpoint still failing")
                    
            else:
                print(f"⚠️  Application not ready: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"⚠️  Application not responding: {e}")
        
        if attempt < 10:
            print("⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    
    print("\n❌ Migration monitoring timeout reached")
    print("💡 Check Render dashboard for deployment logs")
    return False

if __name__ == "__main__":
    monitor_deployment()
