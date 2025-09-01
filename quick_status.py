#!/usr/bin/env python3
"""
⚡ QUICK STATUS - STRIPE CREDITS SYSTEM
======================================

Schneller Status-Check des gesamten Systems.
Zeigt Deployment-Status und nächste Schritte.
"""

import requests
import time
from datetime import datetime

def quick_status():
    print("⚡ QUICK STATUS - STRIPE CREDITS SYSTEM")
    print("="*50)
    print(f"🕒 Zeit: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    # Backend Check
    try:
        response = requests.get("https://resume-matcher-backend-j06k.onrender.com/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend: ONLINE")
            backend_online = True
        else:
            print(f"❌ Backend: ERROR ({response.status_code})")
            backend_online = False
    except:
        print("🔌 Backend: DEPLOYMENT LÄUFT...")
        backend_online = False
    
    # Frontend Check  
    try:
        response = requests.get("https://gojob.ing/api/auth/session", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend: ONLINE")
        else:
            print(f"⚠️ Frontend: STATUS {response.status_code}")
    except:
        print("❌ Frontend: NICHT ERREICHBAR")
    
    print()
    
    if backend_online:
        print("🎉 SYSTEM IST BEREIT!")
        print("📋 NÄCHSTE SCHRITTE:")
        print("   1. Melden Sie sich bei https://gojob.ing an")
        print("   2. Testen Sie einen Kauf")
        print("   3. python final_stripe_credits_live_diagnose.py")
    else:
        print("⏳ DEPLOYMENT LÄUFT NOCH...")
        print("📋 AKTIONEN:")
        print("   • Deployment Monitor läuft automatisch")
        print("   • python deployment_monitor.py (falls gestoppt)")
        print("   • Check Render Dashboard: https://dashboard.render.com")
    
    print()
    print("🔧 ANGEWENDETE FIXES:")
    print("   ✅ Checkout Session Metadata verbessert")
    print("   ✅ Webhook User-ID Resolution verbessert") 
    print("   ✅ Umfassende Debugging-Tools erstellt")
    print("   ✅ Environment Variables Template")

if __name__ == "__main__":
    quick_status()
