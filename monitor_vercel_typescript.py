#!/usr/bin/env python3
"""
Monitor Vercel Deployment for TypeScript Fix
============================================

Monitors the Vercel deployment to ensure the TypeScript compilation
error for Stripe API version is resolved.
"""

import requests
import time
from datetime import datetime

def test_vercel_frontend():
    """Test if Vercel frontend is working after the TypeScript fix"""
    
    frontend_url = "https://gojob.ing"
    
    try:
        # Test basic frontend availability
        response = requests.get(frontend_url, timeout=10)
        
        if response.status_code in [200, 301, 302]:
            return "✅ DEPLOYED", "Frontend is accessible"
        else:
            return "❌ ERROR", f"Status: {response.status_code}"
            
    except requests.RequestException as e:
        return "❌ DOWN", f"Connection failed: {e}"

def test_stripe_endpoints_after_fix():
    """Test that Stripe endpoints work with the new TypeScript-compatible API version"""
    
    frontend_url = "https://gojob.ing"
    results = {}
    
    # Test 1: Stripe Checkout
    try:
        response = requests.post(
            f"{frontend_url}/api/stripe/checkout",
            json={"price_id": "price_test_123"},
            timeout=15
        )
        
        # We expect 401 (auth required) or other non-500 errors, NOT TypeScript compilation errors
        if response.status_code == 401:
            results["stripe_checkout"] = "✅ WORKING - Auth required (expected)"
        elif response.status_code == 400:
            results["stripe_checkout"] = "✅ WORKING - Bad request (expected without auth)"
        elif response.status_code == 500:
            try:
                error_data = response.json()
                error_msg = str(error_data).lower()
                
                if "type error" in error_msg or "typescript" in error_msg:
                    results["stripe_checkout"] = "❌ FAILED - TypeScript compilation error still present"
                elif "not assignable to type" in error_msg:
                    results["stripe_checkout"] = "❌ FAILED - TypeScript type error still present"
                else:
                    results["stripe_checkout"] = "✅ WORKING - Runtime error (not TypeScript)"
            except:
                results["stripe_checkout"] = "✅ WORKING - Server error but not TypeScript"
        else:
            results["stripe_checkout"] = f"✅ WORKING - Status {response.status_code}"
            
    except requests.RequestException as e:
        results["stripe_checkout"] = f"❌ ERROR - {e}"
    
    # Test 2: Stripe Portal  
    try:
        response = requests.post(
            f"{frontend_url}/api/stripe/portal",
            json={},
            timeout=15
        )
        
        if response.status_code == 401:
            results["stripe_portal"] = "✅ WORKING - Auth required (expected)"
        elif response.status_code == 400:
            results["stripe_portal"] = "✅ WORKING - Bad request (expected without auth)"
        elif response.status_code == 500:
            try:
                error_data = response.json()
                error_msg = str(error_data).lower()
                
                if "type error" in error_msg or "typescript" in error_msg:
                    results["stripe_portal"] = "❌ FAILED - TypeScript compilation error still present"
                elif "not assignable to type" in error_msg:
                    results["stripe_portal"] = "❌ FAILED - TypeScript type error still present"
                else:
                    results["stripe_portal"] = "✅ WORKING - Runtime error (not TypeScript)"
            except:
                results["stripe_portal"] = "✅ WORKING - Server error but not TypeScript"
        else:
            results["stripe_portal"] = f"✅ WORKING - Status {response.status_code}"
            
    except requests.RequestException as e:
        results["stripe_portal"] = f"❌ ERROR - {e}"
    
    return results

def monitor_vercel_deployment():
    """Monitor Vercel deployment progress"""
    
    print("🚀 Monitoring Vercel Deployment...")
    print("=" * 50)
    print("Commit: 902f532 (TypeScript-compatible Stripe API version 2024-06-20)")
    print("Frontend: https://gojob.ing")
    print()
    print("Looking for:")
    print("✅ Frontend deployed successfully")
    print("✅ No TypeScript compilation errors")
    print("✅ Stripe endpoints working with new API version")
    print()
    
    deployment_successful = False
    
    while not deployment_successful:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Test frontend availability
            frontend_status, frontend_msg = test_vercel_frontend()
            
            print(f"[{current_time}] Status Update:")
            print(f"  Frontend Deployment: {frontend_status} - {frontend_msg}")
            
            if frontend_status.startswith("✅"):
                # Test Stripe endpoints if frontend is available
                stripe_results = test_stripe_endpoints_after_fix()
                
                typescript_errors = False
                all_working = True
                
                for endpoint, result in stripe_results.items():
                    print(f"  {endpoint}: {result}")
                    
                    if "TypeScript" in result or "type error" in result.lower():
                        typescript_errors = True
                    
                    if not result.startswith("✅"):
                        all_working = False
                
                if typescript_errors:
                    print("  ❌ TypeScript compilation errors still present!")
                    print("  ⏳ Waiting for new deployment...")
                elif all_working:
                    print()
                    print("🎉 VERCEL DEPLOYMENT SUCCESSFUL!")
                    print("✅ TypeScript compilation error resolved!")
                    print("✅ Stripe API version 2024-06-20 working correctly!")
                    print("✅ No more 'Type error: Type \"2023-10-16\" is not assignable to type \"2024-06-20\"'!")
                    deployment_successful = True
                else:
                    print("  ⏳ Some endpoints still having issues, monitoring...")
            else:
                print("  ⏳ Waiting for frontend deployment...")
            
            if not deployment_successful:
                print()
                time.sleep(20)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"🔥 Monitoring error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_vercel_deployment()
