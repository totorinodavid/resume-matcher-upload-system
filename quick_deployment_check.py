#!/usr/bin/env python3
"""
🔍 RENDER DEPLOYMENT STATUS CHECKER
Quick check of Render deployment status and logs
"""

import requests
import time
from datetime import datetime

def check_deployment_status():
    """Check if the app is deployed and what's happening"""
    base_url = "https://resume-matcher-backend.onrender.com"
    
    print("🔍 RENDER DEPLOYMENT STATUS CHECK")
    print("=" * 50)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: {base_url}")
    print("-" * 50)
    
    # Try different endpoints to understand the deployment state
    endpoints_to_test = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/docs", "API documentation"),
        ("/api/v1/health", "API health"),
    ]
    
    for endpoint, description in endpoints_to_test:
        try:
            print(f"\n📍 Testing {description}: {endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(list(response.headers.items())[:3])}")
            
            # Check content
            content = response.text[:200]
            if "render" in content.lower() or "error" in content.lower():
                print(f"   Content preview: {content}")
            else:
                print(f"   Content length: {len(response.text)} chars")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout - deployment likely in progress")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection error - deployment likely starting")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("📋 ANALYSIS:")
    
    # Try to determine deployment status
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ App is LIVE and responding!")
        elif response.status_code == 404:
            print("⏳ App deployed but routes not ready (building/starting)")
        elif response.status_code >= 500:
            print("❌ App deployed but has internal errors")
        else:
            print(f"🤔 Unexpected status: {response.status_code}")
    except:
        print("⏳ App not yet accessible - deployment in progress")
    
    print("💡 Next steps:")
    print("   • Render deployments typically take 2-5 minutes")
    print("   • Monitor will continue checking automatically")
    print("   • Check Render dashboard for detailed logs if needed")

if __name__ == "__main__":
    check_deployment_status()
