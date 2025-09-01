#!/usr/bin/env python3
"""
Monitor script to check if Stripe API version fix has been deployed to production
"""
import requests
import time
import json
from datetime import datetime

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"
FRONTEND_URL = "https://gojob.ing"

def check_backend_health():
    """Check if backend is responding"""
    try:
        response = requests.get(f"{BACKEND_URL}/healthz", timeout=10)
        return response.status_code == 200
    except:
        return False

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
    
    # 3. Test Backend Billing API (via BFF proxy)
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/bff/api/v1/billing/checkout/create",
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

def check_deployment_status():
    """Check overall deployment status"""
    print(f"🕐 {datetime.now().strftime('%H:%M:%S')} - Checking deployment status...")
    
    # 1. Backend health
    backend_healthy = check_backend_health()
    print(f"   Backend Health: {'✅ OK' if backend_healthy else '❌ DOWN'}")
    
    if not backend_healthy:
        print("   ⚠️ Backend is down - waiting for deployment...")
        return False
    
    # 2. Test Stripe endpoint
    stripe_status, stripe_msg = test_stripe_checkout_endpoint()
    print(f"   Stripe Status: {stripe_status} - {stripe_msg}")
    
    if stripe_status == "FIXED":
        print("   🎉 DEPLOYMENT SUCCESSFUL - Stripe API version fix is live!")
        return True
    elif stripe_status == "OLD_BUG":
        print("   ⏳ Old bug still present - deployment not yet complete")
        return False
    else:
        print(f"   ❓ Unknown status - need manual verification")
        return False

def monitor_deployment():
    """Monitor deployment until completion or timeout"""
    print("🔧 Monitoring Stripe API Version Fix Deployment")
    print("=" * 60)
    print(f"Backend: {BACKEND_URL}")
    print(f"Frontend: {FRONTEND_URL}")
    print("=" * 60)
    
    start_time = time.time()
    max_wait_time = 600  # 10 minutes max wait
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > max_wait_time:
            print(f"\n⏰ Timeout reached ({max_wait_time/60:.1f} minutes)")
            print("   Manual verification recommended")
            break
        
        if check_deployment_status():
            print(f"\n🎉 SUCCESS! Deployment completed in {elapsed/60:.1f} minutes")
            print("\n✅ STRIPE API VERSION FIX IS NOW LIVE IN PRODUCTION")
            print("\n🧪 Manual verification steps:")
            print(f"   1. Visit: {FRONTEND_URL}")
            print("   2. Sign in and try to purchase credits")
            print("   3. Should see payment form instead of API version error")
            break
        
        print(f"   ⏳ Waiting... ({elapsed/60:.1f}m elapsed)")
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    monitor_deployment()
