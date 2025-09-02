"""
🚨 LIVE DEPLOYMENT MONITOR
Überwacht die Deployment bis es funktioniert
"""
import requests
import time
from datetime import datetime

def check_deployment():
    """Check if deployment is working"""
    url = "https://resume-matcher-backend-j06k.onrender.com/health"
    try:
        response = requests.get(url, timeout=10)
        return response.status_code, response.text if response.status_code == 200 else f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return 0, str(e)

def monitor_deployment():
    """Monitor deployment until it works"""
    print("🚨 LIVE DEPLOYMENT MONITOR")
    print("🎯 Target: https://resume-matcher-backend-j06k.onrender.com/health")
    print("=" * 60)
    
    start_time = time.time()
    check_count = 0
    
    while True:
        check_count += 1
        elapsed = int(time.time() - start_time)
        
        print(f"\n[{elapsed:03d}s] 🔍 Check #{check_count}")
        
        status_code, response_text = check_deployment()
        
        if status_code == 200:
            print("🎉 SUCCESS! Backend is LIVE!")
            print(f"✅ Response: {response_text}")
            print(f"🕒 Total time: {elapsed} seconds")
            print("🚀 PRODUCTION IS ONLINE!")
            break
        elif status_code == 502:
            print("⚠️  502 Bad Gateway - Render is still starting up...")
        elif status_code == 404:
            print("⚠️  404 Not Found - Still deploying...")
        else:
            print(f"⚠️  Status: {status_code} - {response_text}")
        
        if elapsed > 600:  # 10 minutes
            print("❌ TIMEOUT - Manual intervention needed")
            break
            
        print("⏳ Waiting 15s for next check...")
        time.sleep(15)

if __name__ == "__main__":
    monitor_deployment()
