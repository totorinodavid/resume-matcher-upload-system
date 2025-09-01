#!/usr/bin/env python3
"""
Monitor Stripe API Version Fix Deployment
==========================================

Monitors both frontend and backend Stripe endpoints to verify the 
'Invalid Stripe API version: 2024-12-18' error has been fixed.

Expected behavior after fix:
- Frontend /api/stripe/checkout should work (401 auth error is OK)
- Frontend /api/stripe/portal should work (401 auth error is OK) 
- Backend billing endpoints should work (401/403 auth error is OK)
- No more "Invalid Stripe API version" errors
"""

import requests
import time
from datetime import datetime

# Production URLs
FRONTEND_URL = "https://gojob.ing"
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def test_backend_health():
    """Test if backend is responsive"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            return "HEALTHY", "Backend is responsive"
        else:
            return "UNHEALTHY", f"Status: {response.status_code}"
    except requests.RequestException as e:
        return "DOWN", f"Connection failed: {e}"

def test_stripe_endpoints():
    """Test both frontend and backend Stripe endpoints for API version errors"""
    results = {}
    
    # 1. Test Frontend Stripe Checkout (Next.js API route)
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/stripe/checkout",
            json={"price_id": "price_test_123"},
            timeout=10
        )
        
        if response.status_code == 401:
            results["frontend_checkout"] = ("FIXED", "Expected auth error (401)")
        elif response.status_code == 500:
            try:
                error_data = response.json()
                if "Invalid Stripe API version" in str(error_data):
                    results["frontend_checkout"] = ("OLD_BUG", "Stripe API version error in frontend")
                else:
                    results["frontend_checkout"] = ("UNKNOWN", f"Different 500 error: {error_data}")
            except:
                results["frontend_checkout"] = ("UNKNOWN", "500 error but can't parse response")
        else:
            results["frontend_checkout"] = ("UNKNOWN", f"Unexpected status: {response.status_code}")
            
    except requests.RequestException as e:
        results["frontend_checkout"] = ("ERROR", f"Request failed: {e}")
    
    # 2. Test Frontend Stripe Portal
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/stripe/portal",
            json={},
            timeout=10
        )
        
        if response.status_code == 401:
            results["frontend_portal"] = ("FIXED", "Expected auth error (401)")
        elif response.status_code == 500:
            try:
                error_data = response.json()
                if "Invalid Stripe API version" in str(error_data):
                    results["frontend_portal"] = ("OLD_BUG", "Stripe API version error in portal")
                else:
                    results["frontend_portal"] = ("UNKNOWN", f"Different 500 error: {error_data}")
            except:
                results["frontend_portal"] = ("UNKNOWN", "500 error but can't parse response")
        else:
            results["frontend_portal"] = ("UNKNOWN", f"Unexpected status: {response.status_code}")
            
    except requests.RequestException as e:
        results["frontend_portal"] = ("ERROR", f"Request failed: {e}")
    
    # 3. Test Backend Billing API (direct)
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/billing/checkout/create",
            json={"price_id": "price_test_123"},
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            results["backend_billing"] = ("FIXED", f"Expected auth error ({response.status_code})")
        elif response.status_code == 500:
            try:
                error_data = response.json()
                if "Invalid Stripe API version" in str(error_data):
                    results["backend_billing"] = ("OLD_BUG", "Stripe API version error in backend")
                else:
                    results["backend_billing"] = ("UNKNOWN", f"Different 500 error: {error_data}")
            except:
                results["backend_billing"] = ("UNKNOWN", "500 error but can't parse response")
        else:
            results["backend_billing"] = ("UNKNOWN", f"Unexpected status: {response.status_code}")
            
    except requests.RequestException as e:
        results["backend_billing"] = ("ERROR", f"Request failed: {e}")
    
    return results

def monitor_deployment():
    """Main monitoring loop"""
    print("🔍 Monitoring Stripe API Version Fix Deployment...")
    print("=" * 60)
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    print("Looking for:")
    print("✅ Frontend /api/stripe/checkout works (no API version error)")
    print("✅ Frontend /api/stripe/portal works (no API version error)")
    print("✅ Backend billing endpoints work (no API version error)")
    print()
    
    fixed_endpoints = set()
    
    while True:
        try:
            # Test backend health
            backend_status, backend_msg = test_backend_health()
            
            # Test Stripe endpoints for API version errors
            stripe_results = test_stripe_endpoints()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"[{current_time}] Status Update:")
            print(f"  Backend Health: {backend_status} - {backend_msg}")
            
            # Report Stripe endpoint tests
            has_old_bug = False
            for endpoint, (status, msg) in stripe_results.items():
                icon = "✅" if status == "FIXED" else "⚠️" if status == "OLD_BUG" else "❌"
                print(f"  {icon} {endpoint}: {status} - {msg}")
                
                if status == "FIXED":
                    fixed_endpoints.add(endpoint)
                elif status == "OLD_BUG":
                    has_old_bug = True
                    print(f"       🚨 {endpoint} still has Stripe API version bug!")
            
            # Check if critical endpoints are fixed
            if not has_old_bug and "frontend_checkout" in fixed_endpoints:
                print()
                print("🎉 DEPLOYMENT SUCCESSFUL!")
                print("✅ Stripe API version fix is now LIVE!")
                print("✅ No more 'Invalid Stripe API version: 2024-12-18' errors!")
                print("✅ Payment system should now work correctly!")
                break
            
            print(f"   📊 Progress: {len(fixed_endpoints)} endpoints confirmed fixed")
            if has_old_bug:
                print("   ⏳ Waiting for deployment to complete...")
            else:
                print("   ⏳ Verifying all endpoints...")
            
            print()
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"🔥 Monitoring error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_deployment()
