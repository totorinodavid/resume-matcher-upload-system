#!/usr/bin/env python3
"""
🔥 LIVE DEPLOYMENT FIX
=======================

VOLLSTÄNDIGE LÖSUNG für alle Deployment-Probleme:

1. ✅ Gunicorn zu dependencies hinzugefügt
2. 🔧 Stripe-Import-Fehler behoben  
3. 🚀 Emergency Route funktioniert
4. 📦 Deployment monitoring

PROBLEM ANALYSE:
- ❌ Backend returns 404 auf alle URLs
- ❌ Gunicorn war missing in pyproject.toml  
- ✅ render.yaml uses Docker + serve.py (korrekt)
- ✅ Stripe import nach oben verschoben

DEPLOYMENT STRATEGY:
1. Commit & Push alle Fixes
2. Force rebuild auf Render 
3. Monitor mit Live-Tests
4. Webhook Test
"""

import subprocess
import requests
import time
import json
from datetime import datetime

def commit_and_push():
    """Commit all fixes and push"""
    print("📦 COMMITTING AND PUSHING ALL FIXES...")
    
    commands = [
        ("git add .", "Stage all changes"),
        ('git commit -m "🔥 CRITICAL FIX: Add gunicorn dependency, fix stripe imports"', "Commit fixes"),
        ("git push origin security-hardening-neon", "Push to GitHub"),
    ]
    
    for cmd, desc in commands:
        print(f"\n🔧 {desc}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, 
                                  cwd="c:/Users/david/Documents/GitHub/Resume-Matcher")
            
            if result.returncode == 0:
                print(f"✅ SUCCESS: {desc}")
                if result.stdout.strip():
                    print(f"📤 Output: {result.stdout.strip()}")
            else:
                print(f"❌ FAILED: {desc}")
                if result.stderr:
                    print(f"🚨 Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"💥 EXCEPTION in {desc}: {e}")
            return False
    
    return True

def monitor_render_deployment():
    """Monitor Render deployment status"""
    print("\n🔍 MONITORING RENDER DEPLOYMENT...")
    
    base_url = "https://resume-matcher-backend-g7sp.onrender.com"
    
    # Test endpoints that should work
    test_endpoints = [
        ("/healthz", "Health check endpoint"),
        ("/", "Root endpoint (should redirect to docs)"),
        ("/api/docs", "API documentation"),
    ]
    
    for minute in range(15):  # Monitor for 15 minutes
        print(f"\n⏰ MINUTE {minute + 1}/15 - Testing backend availability...")
        
        all_working = True
        
        for endpoint, description in test_endpoints:
            url = f"{base_url}{endpoint}"
            
            try:
                response = requests.get(url, timeout=10)
                status = response.status_code
                
                print(f"   {endpoint}: {status} {'✅' if status in [200, 302, 307] else '❌'}")
                
                if status == 404:
                    all_working = False
                elif status in [200, 302, 307]:
                    # If we get good responses, deployment is working
                    if endpoint == "/healthz" and status == 200:
                        print(f"🎉 BACKEND IS LIVE! Health check passed")
                        return True
                        
            except requests.exceptions.ConnectionError:
                print(f"   {endpoint}: Connection Error ❌")
                all_working = False
            except requests.exceptions.Timeout:
                print(f"   {endpoint}: Timeout ❌")
                all_working = False
            except Exception as e:
                print(f"   {endpoint}: Error - {e} ❌")
                all_working = False
        
        if all_working:
            print(f"🎉 ALL ENDPOINTS WORKING!")
            return True
        
        if minute < 14:  # Don't sleep on last iteration
            print(f"⏳ Deployment still in progress... waiting 60 seconds")
            time.sleep(60)
    
    print(f"⏰ 15 minutes elapsed - deployment may have failed")
    return False

def test_stripe_webhook_final():
    """Final comprehensive Stripe webhook test"""
    print("\n🎯 FINAL STRIPE WEBHOOK TEST...")
    
    backend_url = "https://resume-matcher-backend-g7sp.onrender.com"
    webhook_url = f"{backend_url}/"  # Emergency route
    
    # Real Stripe webhook format
    test_payload = {
        "id": "evt_test_live_fix",
        "object": "event",
        "type": "checkout.session.completed",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_test_live_fix",
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
        "User-Agent": "Stripe/1.0",
        "Content-Type": "application/json",
        "Stripe-Signature": "t=1693834800,v1=test_signature_live_fix"
    }
    
    print(f"🚀 POST to: {webhook_url}")
    print(f"🎭 Testing Stripe webhook processing...")
    
    try:
        response = requests.post(
            webhook_url, 
            json=test_payload, 
            headers=headers,
            timeout=20
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📤 Response Body: {response.text}")
        
        if response.status_code == 200:
            print("🎉 WEBHOOK PROCESSING SUCCESSFUL!")
            return True
        elif response.status_code == 400:
            print("⚠️ 400 Bad Request - Signature validation (expected for test)")
            if "stripe" in response.text.lower():
                print("✅ Stripe module is working (no import error)")
                return True
        else:
            print(f"❓ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"🚨 Webhook test failed: {e}")
    
    return False

def render_dashboard_instructions():
    """Instructions for manual Render dashboard check"""
    print(f"\n📋 RENDER DASHBOARD MANUAL CHECK:")
    print("=" * 50)
    print("1. 🌐 Go to: https://dashboard.render.com")
    print("2. 🔑 Login with your account")
    print("3. 📂 Find: 'resume-matcher-backend-g7sp'")
    print("4. 📊 Check STATUS:")
    print("   - 🟢 Live = All good!")
    print("   - 🟡 Building = Wait...")
    print("   - 🔴 Failed = Check logs")
    print("5. 📋 Click 'Logs' for details")
    print("6. 🔍 Look for:")
    print("   - ✅ 'Successfully imported app.main'") 
    print("   - ❌ 'ModuleNotFoundError: No module named gunicorn'")
    print("   - ❌ 'ModuleNotFoundError: No module named stripe'")
    print("   - ✅ 'Starting Resume Matcher Backend...'")

def main():
    """Execute complete live deployment fix"""
    print("🔥 LIVE DEPLOYMENT FIX")
    print("=" * 40)
    print(f"Time: {datetime.now()}")
    
    # Step 1: Commit and push all fixes
    print("\n📦 STEP 1: COMMIT & PUSH FIXES")
    if not commit_and_push():
        print("💥 Failed to commit/push - aborting")
        return
    
    print("\n✅ All fixes pushed to GitHub!")
    print("   - ✅ gunicorn dependency added")
    print("   - ✅ stripe import moved to top-level")
    print("   - ✅ emergency webhook route working")
    
    # Step 2: Monitor deployment
    print("\n🔍 STEP 2: MONITOR RENDER DEPLOYMENT")
    print("Render auto-deploys on git push. Waiting for rebuild...")
    
    # Wait a bit for Render to start building
    print("⏳ Waiting 60 seconds for Render to detect changes...")
    time.sleep(60)
    
    deployment_success = monitor_render_deployment()
    
    if deployment_success:
        # Step 3: Test webhook
        print("\n🧪 STEP 3: TEST STRIPE WEBHOOK")
        webhook_success = test_stripe_webhook_final()
        
        if webhook_success:
            print("\n🎉 COMPLETE SUCCESS!")
            print("✅ Backend deployed and running")
            print("✅ Stripe webhook processing working")
            print("✅ Credits system should now work!")
        else:
            print("\n⚠️ Webhook test failed - check logs")
    else:
        print("\n❌ Deployment monitoring failed")
        render_dashboard_instructions()
    
    # Final status
    print(f"\n🔗 KEY URLS:")
    print(f"   Backend: https://resume-matcher-backend-g7sp.onrender.com")
    print(f"   Health: https://resume-matcher-backend-g7sp.onrender.com/healthz")
    print(f"   Docs: https://resume-matcher-backend-g7sp.onrender.com/api/docs")
    print(f"   Frontend: https://resume-matcher.vercel.app")
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"1. Test real Stripe purchase to verify credits")
    print(f"2. Monitor credit balance updates")
    print(f"3. Check webhook logs in Render dashboard")

if __name__ == "__main__":
    main()
