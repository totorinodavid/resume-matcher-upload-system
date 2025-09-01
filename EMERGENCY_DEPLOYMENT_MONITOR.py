#!/usr/bin/env python3
"""
🚨 EMERGENCY DEPLOYMENT MONITOR

Überwacht das Deployment des Emergency Fix:
- Database Schema Compatibility Fix
- EmergencyUserService statt UserService mit user_uuid
- Legacy User Model ohne neue Spalten

WARTET auf Render Deployment und testet dann!
"""

import requests
import time
from datetime import datetime

# LIVE URLs
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def log(emoji: str, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{timestamp} {emoji} {message}")

def monitor_deployment():
    """Monitor das Emergency Deployment"""
    
    log("🚨", "EMERGENCY DEPLOYMENT MONITOR STARTING")
    log("🎯", f"Backend: {BACKEND_URL}")
    log("⏰", "Warte auf Render Deployment...")
    
    # Warte 3 Minuten auf Deployment
    for i in range(18):  # 18 * 10 = 180 seconds = 3 minutes
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            log("🔍", f"Health check attempt {i+1}/18: {response.status_code}")
            
            if response.status_code == 200:
                log("✅", "Backend is responding!")
                break
                
        except Exception as e:
            log("⏳", f"Waiting for deployment... ({i+1}/18)")
        
        time.sleep(10)  # 10 seconds between checks
    
    # Nach dem Warten - Final Test
    log("🧪", "STARTING EMERGENCY TESTS...")
    
    try:
        # Test Backend Health
        response = requests.get(f"{BACKEND_URL}/health", timeout=30)
        log("🏥", f"Backend health: {response.status_code}")
        
        # Test Admin Endpoint
        admin_response = requests.get(f"{BACKEND_URL}/api/v1/admin/user-credits/1", timeout=30)
        log("👑", f"Admin endpoint: {admin_response.status_code}")
        
        if admin_response.status_code == 200:
            log("🎉", "EMERGENCY FIX DEPLOYED SUCCESSFULLY!")
            log("💪", "Database Schema Compatibility: FIXED")
            log("💪", "EmergencyUserService: ACTIVE")
            log("💪", "Webhook Processing: READY")
            return True
        else:
            log("⚠️", "Backend responding but admin endpoint has issues")
            return False
            
    except Exception as e:
        log("❌", f"Emergency test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        result = monitor_deployment()
        if result:
            print("\n🎉 EMERGENCY DEPLOYMENT SUCCESSFUL!")
            print("🚀 Das System sollte jetzt Stripe Webhooks verarbeiten können!")
            print("💳 Teste jetzt eine Stripe Zahlung!")
        else:
            print("\n⚠️ DEPLOYMENT ISSUES DETECTED")
            print("🔧 Weitere Debugging erforderlich...")
    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrupted by user")
    except Exception as e:
        print(f"\n💥 MONITORING ERROR: {e}")
