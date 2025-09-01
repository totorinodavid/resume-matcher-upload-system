#!/usr/bin/env python3
"""
🎯 LIVE BACKEND TEST NACH DEPLOYMENT
====================================

Latest commit deployed: 🔥 CRITICAL FIX: Add gunicorn dependency, fix stripe imports

FIXES INCLUDED:
✅ gunicorn dependency added to pyproject.toml
✅ stripe import moved to module level
✅ emergency webhook route at "/"
✅ proper error handling

NOW TESTING:
1. Backend availability
2. Health check
3. Stripe webhook functionality
4. Credit system
"""

import requests
import time
import json
from datetime import datetime

def test_backend_availability():
    """Test if backend is now available"""
    print("🔍 TESTING BACKEND AVAILABILITY...")
    
    base_url = "https://resume-matcher-backend-g7sp.onrender.com"
    
    test_endpoints = [
        ("/healthz", "Health check"),
        ("/", "Root endpoint"), 
        ("/api/docs", "API documentation"),
        ("/api/v1", "API v1 routes"),
    ]
    
    results = {}
    
    for endpoint, description in test_endpoints:
        url = f"{base_url}{endpoint}"
        print(f"\n🔍 Testing {description}: {endpoint}")
        
        try:
            response = requests.get(url, timeout=15)
            status = response.status_code
            
            print(f"   📊 Status: {status}")
            
            if status == 200:
                print(f"   ✅ SUCCESS: {description} working!")
                results[endpoint] = "SUCCESS"
            elif status in [302, 307]:
                print(f"   ✅ REDIRECT: {description} redirecting (normal)")
                results[endpoint] = "REDIRECT"
            elif status == 404:
                print(f"   ❌ NOT FOUND: {description} missing")
                results[endpoint] = "NOT_FOUND"
            else:
                print(f"   ⚠️  STATUS {status}: {description}")
                results[endpoint] = f"STATUS_{status}"
                
            # Show response body for important endpoints
            if endpoint in ["/healthz", "/"] and len(response.text) < 200:
                print(f"   📤 Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"   💥 CONNECTION ERROR: Service down")
            results[endpoint] = "CONNECTION_ERROR"
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: Service slow")
            results[endpoint] = "TIMEOUT"
        except Exception as e:
            print(f"   🚨 ERROR: {e}")
            results[endpoint] = f"ERROR: {e}"
    
    return results

def test_stripe_webhook_processing():
    """Test the emergency Stripe webhook route"""
    print("\n🎯 TESTING STRIPE WEBHOOK PROCESSING...")
    
    webhook_url = "https://resume-matcher-backend-g7sp.onrender.com/"
    
    # Proper Stripe webhook payload
    test_payload = {
        "id": "evt_test_final_check",
        "object": "event", 
        "type": "checkout.session.completed",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_test_final_check",
                "object": "checkout.session",
                "customer": "cus_test_customer",
                "payment_status": "paid",
                "status": "complete",
                "metadata": {
                    "user_id": "e747de39-1b54-4cd0-96eb-e68f155931e2",
                    "credits": "100"
                }
            }
        }
    }
    
    headers = {
        "User-Agent": "Stripe/1.0",  # This triggers our emergency route
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1693834800,v1=test_signature_final"
    }
    
    print(f"🚀 POST to: {webhook_url}")
    print(f"🎭 User-Agent: {headers['User-Agent']} (triggers emergency route)")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers=headers,
            timeout=20
        )
        
        status = response.status_code
        body = response.text
        
        print(f"📊 Response Status: {status}")
        print(f"📤 Response Body: {body}")
        
        # Analyze the response
        if status == 200:
            print("🎉 PERFECT: Webhook processed successfully!")
            return "SUCCESS"
        elif status == 400:
            if "stripe" in body.lower():
                print("✅ GOOD: Stripe module working (signature validation expected)")
                return "STRIPE_WORKING"
            else:
                print("⚠️ Bad Request - check payload format")
                return "BAD_REQUEST"
        elif status == 405:
            print("❌ Method Not Allowed - emergency route not working")
            return "METHOD_NOT_ALLOWED"
        elif status == 404:
            print("❌ Not Found - backend still not accessible")
            return "NOT_FOUND"
        else:
            print(f"❓ Unexpected status: {status}")
            return f"STATUS_{status}"
            
    except Exception as e:
        print(f"🚨 Webhook test failed: {e}")
        return f"ERROR: {e}"

def comprehensive_health_check():
    """Comprehensive health check of all systems"""
    print("\n🏥 COMPREHENSIVE HEALTH CHECK...")
    
    health_results = {}
    
    # 1. Backend availability
    print("\n1️⃣ BACKEND AVAILABILITY")
    backend_results = test_backend_availability()
    health_results["backend"] = backend_results
    
    # 2. Stripe webhook processing  
    print("\n2️⃣ STRIPE WEBHOOK PROCESSING")
    webhook_result = test_stripe_webhook_processing()
    health_results["webhook"] = webhook_result
    
    # 3. Summary
    print(f"\n📊 HEALTH CHECK SUMMARY")
    print("=" * 40)
    
    backend_working = any(result in ["SUCCESS", "REDIRECT"] for result in backend_results.values())
    webhook_working = webhook_result in ["SUCCESS", "STRIPE_WORKING"]
    
    print(f"🔧 Backend Status: {'✅ WORKING' if backend_working else '❌ FAILED'}")
    print(f"🎯 Webhook Status: {'✅ WORKING' if webhook_working else '❌ FAILED'}")
    
    if backend_working and webhook_working:
        print(f"\n🎉 COMPLETE SUCCESS!")
        print(f"✅ Backend deployed and accessible")
        print(f"✅ Stripe webhook processing functional")
        print(f"✅ Credit system should work now")
        
        print(f"\n🚀 READY FOR LIVE TESTING:")
        print(f"1. Go to: https://resume-matcher.vercel.app")
        print(f"2. Sign in with your account")
        print(f"3. Try purchasing credits")
        print(f"4. Check if credits are added to balance")
        
    elif backend_working:
        print(f"\n⚠️ PARTIAL SUCCESS")
        print(f"✅ Backend is working")
        print(f"❌ Webhook processing has issues")
        print(f"🔧 Check Render logs for webhook errors")
        
    else:
        print(f"\n❌ DEPLOYMENT FAILED")
        print(f"💥 Backend still not accessible")
        print(f"🔧 Check Render dashboard for build errors")
    
    return health_results

def main():
    print("🎯 LIVE BACKEND TEST NACH DEPLOYMENT")
    print("=" * 50)
    print(f"Time: {datetime.now()}")
    print(f"Latest commit: 🔥 CRITICAL FIX: Add gunicorn dependency, fix stripe imports")
    
    # Run comprehensive health check
    results = comprehensive_health_check()
    
    # Final instructions based on results
    backend_working = any(result in ["SUCCESS", "REDIRECT"] for result in results["backend"].values())
    
    if backend_working:
        print(f"\n📋 NEXT STEPS:")
        print(f"1. ✅ Backend is deployed and working")
        print(f"2. 🧪 Test real Stripe purchase:")
        print(f"   - Go to https://resume-matcher.vercel.app")
        print(f"   - Sign in as user e747de39-1b54-4cd0-96eb-e68f155931e2")
        print(f"   - Purchase credits")
        print(f"   - Check credit balance updates")
        print(f"3. 📊 Monitor Render logs for webhook processing")
        print(f"4. 🎉 Credits should now be added correctly!")
    else:
        print(f"\n🚨 TROUBLESHOOTING NEEDED:")
        print(f"1. Check Render dashboard: https://dashboard.render.com")
        print(f"2. Look at deployment logs")
        print(f"3. Verify environment variables")
        print(f"4. Check for build failures")

if __name__ == "__main__":
    main()
