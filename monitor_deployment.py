#!/usr/bin/env python3
"""
Monitor deployment status and test when ready
"""

import time
import json
from urllib.request import urlopen, Request, HTTPError
from urllib.error import URLError

def test_admin_endpoint():
    url = "https://resume-matcher-backend-j06k.onrender.com/admin/credits/e747de39-1b54-4cd0-96eb-e68f155931e2"
    
    try:
        request = Request(url)
        with urlopen(request, timeout=15) as response:
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            
            if status_code == 200:
                data = json.loads(content)
                return True, f"SUCCESS! Balance: {data['total_credits']} credits"
            else:
                return False, f"Status {status_code}: {content}"
                
    except HTTPError as e:
        error_content = e.read().decode('utf-8')
        if "'CreditsService' object has no attribute 'get_user_credits'" in error_content:
            return False, "Old code still deployed"
        return False, f"HTTP Error {e.code}: {error_content}"
    except Exception as e:
        return False, f"Error: {e}"

def monitor_deployment():
    print("🚀 MONITORING DEPLOYMENT STATUS")
    print("=" * 40)
    print("Checking every 30 seconds...")
    print()
    
    for attempt in range(10):  # Check for up to 5 minutes
        print(f"Attempt {attempt + 1}/10...")
        
        success, message = test_admin_endpoint()
        
        if success:
            print("✅ DEPLOYMENT SUCCESSFUL!")
            print(f"   {message}")
            print()
            print("🎉 NOW READY TO TRANSFER CREDITS!")
            return True
        else:
            print(f"   {message}")
        
        if attempt < 9:
            print("   Waiting 30 seconds...")
            time.sleep(30)
        print()
    
    print("❌ Deployment taking longer than expected")
    print("   You may need to check Render dashboard or try again later")
    return False

if __name__ == "__main__":
    monitor_deployment()
