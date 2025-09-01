#!/usr/bin/env python3
"""
🚨 RENDER DEPLOYMENT EMERGENCY DIAGNOSTICS
============================================

Backend returns 404 für alle Endpoints - Das ist ein kritisches Deployment-Problem!

MÖGLICHE URSACHEN:
1. ❌ Service ist down/building
2. ❌ Wrong URL oder routing
3. ❌ Build/startup failure
4. ❌ Environment variables missing

SOFORTIGE DIAGNOSE:
"""

import requests
import time
import json
from datetime import datetime

def check_render_status():
    """Comprehensive Render service check"""
    print("🔍 RENDER DEPLOYMENT DIAGNOSTICS")
    print("=" * 50)
    
    base_url = "https://resume-matcher-backend-g7sp.onrender.com"
    
    # Test various URLs to understand the problem
    test_urls = [
        "/",
        "/healthz", 
        "/health",
        "/api",
        "/api/v1",
        "/docs",
        "/openapi.json"
    ]
    
    print(f"🌐 Testing base URL: {base_url}")
    
    for path in test_urls:
        url = f"{base_url}{path}"
        print(f"\n🔍 Testing: {path}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code != 404:
                print(f"   📤 Response: {response.text[:200]}...")
                if response.headers:
                    print(f"   📋 Server: {response.headers.get('server', 'Unknown')}")
                    
        except requests.exceptions.ConnectionError:
            print("   💥 Connection Error - Service may be down")
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout - Service slow/unresponsive")
        except Exception as e:
            print(f"   🚨 Error: {e}")
    
    # Test if it's a generic "site not found" vs app-specific 404
    print(f"\n🧪 TESTING INVALID DOMAIN...")
    try:
        fake_response = requests.get("https://definitely-not-a-real-domain-12345.onrender.com", timeout=5)
        print(f"   Fake domain status: {fake_response.status_code}")
    except:
        print("   ✅ Fake domain failed as expected - our domain is valid")

def check_render_alternatives():
    """Check alternative Render URLs"""
    print(f"\n🔄 CHECKING ALTERNATIVE RENDER URLS...")
    
    # Sometimes Render has different URL patterns
    alternative_urls = [
        "https://resume-matcher-backend.onrender.com",
        "https://resume-matcher-backend-g7sp.onrender.com",
        "https://resumematcher-backend.onrender.com",
        "https://resumematcher.onrender.com"
    ]
    
    for url in alternative_urls:
        print(f"\n🔍 Testing alternative: {url}")
        try:
            response = requests.get(f"{url}/healthz", timeout=5)
            print(f"   📊 Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   🎉 FOUND WORKING URL: {url}")
                return url
        except:
            print(f"   ❌ Not reachable")
    
    return None

def render_logs_instructions():
    """Detailed instructions for checking Render logs"""
    print(f"\n📋 RENDER DASHBOARD CHECK:")
    print("1. 🌐 Go to: https://dashboard.render.com")
    print("2. 🔑 Sign in with your account")
    print("3. 📂 Find service: 'resume-matcher-backend-g7sp'")
    print("4. 📊 Check service STATUS:")
    print("   - 🟢 Live = Good")
    print("   - 🟡 Building = Wait 2-5 minutes")
    print("   - 🔴 Failed = Build error")
    print("   - ⚪ Sleeping = Cold start")
    
    print(f"\n🔍 LOGS TO CHECK:")
    print("   - Click 'Logs' tab")
    print("   - Look for recent entries")
    print("   - Search for ERROR or FAILED")
    print("   - Check for startup messages")
    
    print(f"\n🚨 COMMON RENDER ISSUES:")
    print("   - ❌ Build timeout (>15 minutes)")
    print("   - ❌ Missing environment variables")
    print("   - ❌ Invalid Procfile or startup command")
    print("   - ❌ Python version mismatch")
    print("   - ❌ Memory/CPU limits exceeded")

def emergency_troubleshooting():
    """Emergency troubleshooting steps"""
    print(f"\n🚨 EMERGENCY TROUBLESHOOTING:")
    print("=" * 40)
    
    print(f"STEP 1: Verify Render Service Status")
    print(f"  → Dashboard shows service state")
    print(f"  → Recent deployments in activity log")
    
    print(f"\nSTEP 2: Check Environment Variables")
    print(f"  → STRIPE_SECRET_KEY set?")
    print(f"  → DATABASE_URL configured?")
    print(f"  → All required vars present?")
    
    print(f"\nSTEP 3: Validate Build Configuration")
    print(f"  → apps/backend/Procfile exists?")
    print(f"  → Python version in pyproject.toml?")
    print(f"  → Dependencies installable?")
    
    print(f"\nSTEP 4: Manual Redeploy")
    print(f"  → Render Dashboard → Deploy → Manual Deploy")
    print(f"  → Watch build logs in real-time")
    print(f"  → Note any error messages")

def main():
    print("🚨 RENDER DEPLOYMENT EMERGENCY DIAGNOSTICS")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    
    # Basic connectivity check
    check_render_status()
    
    # Try alternative URLs
    working_url = check_render_alternatives()
    
    if working_url:
        print(f"\n🎉 SOLUTION: Use working URL: {working_url}")
    else:
        print(f"\n❌ NO WORKING URLS FOUND")
        render_logs_instructions()
        emergency_troubleshooting()
    
    print(f"\n📞 NEXT ACTIONS:")
    print(f"1. Check Render Dashboard immediately")
    print(f"2. Look at recent deployment logs")
    print(f"3. Verify environment variables")
    print(f"4. Try manual redeploy if needed")
    print(f"5. Report findings for next steps")

if __name__ == "__main__":
    main()
