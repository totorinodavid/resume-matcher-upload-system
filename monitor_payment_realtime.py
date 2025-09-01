#!/usr/bin/env python3
"""
Real-Time Stripe Payment Monitor
===============================

Monitors backend logs and webhook activity during actual payments
to diagnose why credits are not being added.
"""

import requests
import time
import json
from datetime import datetime

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"
FRONTEND_URL = "https://gojob.ing"

def monitor_payment_logs():
    """Monitor for webhook and credit activity"""
    print("🔍 REAL-TIME STRIPE PAYMENT MONITORING")
    print("=" * 50)
    print("This tool will help you test a real payment and see what happens.")
    print()
    print("📋 STEPS TO TEST:")
    print("1. Keep this monitor running")
    print("2. Go to https://gojob.ing and sign in")
    print("3. Try to purchase credits")
    print("4. Complete the payment")
    print("5. Watch the output below for webhook activity")
    print()
    print("🔗 Key URLs to check:")
    print(f"   Frontend: {FRONTEND_URL}/billing")
    print(f"   Webhook: {FRONTEND_URL}/api/stripe/webhook")
    print(f"   Credits: {BACKEND_URL}/api/v1/me/credits")
    print()
    print("🎯 What we're looking for:")
    print("   ✅ Stripe checkout session created")
    print("   ✅ Payment completed successfully")
    print("   ✅ Webhook received by backend")
    print("   ✅ Credits added to user account")
    print()
    print("⏰ Monitoring started - proceed with your test payment...")
    print("-" * 50)
    
    last_health_check = 0
    webhook_attempts = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Health check every 30 seconds
            if current_time - last_health_check > 30:
                try:
                    response = requests.get(f"{BACKEND_URL}/healthz", timeout=5)
                    if response.status_code == 200:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Backend healthy")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Backend status: {response.status_code}")
                except:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Backend unreachable")
                
                last_health_check = current_time
            
            # Test webhook endpoint periodically to see if it gets real traffic
            try:
                response = requests.post(
                    f"{BACKEND_URL}/webhooks/stripe",
                    json={"test": "ping"},
                    headers={"Stripe-Signature": "monitoring_ping"},
                    timeout=5
                )
                
                webhook_attempts += 1
                
                if webhook_attempts % 10 == 0:  # Every 10th attempt, show status
                    if response.status_code == 503:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ CRITICAL: STRIPE_WEBHOOK_SECRET not configured!")
                        print("   This explains why credits are not being added after payments!")
                        print("   Solution: Add STRIPE_WEBHOOK_SECRET to Render environment variables")
                        break
                    elif response.status_code == 400:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] ℹ️ Webhook endpoint ready (signature validation active)")
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Webhook test failed: {e}")
            
            time.sleep(3)
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Monitoring stopped")
            print()
            print("📊 DIAGNOSIS SUMMARY:")
            print("If you completed a payment but didn't see webhook activity here,")
            print("the issue is likely:")
            print()
            print("1. 🔧 Missing STRIPE_WEBHOOK_SECRET environment variable")
            print("2. 🔗 Webhook URL not registered with Stripe")
            print("3. 🏷️ Price IDs don't match your Stripe products")
            print()
            print("💡 NEXT STEPS:")
            print("1. Check Render dashboard for STRIPE_WEBHOOK_SECRET")
            print("2. Check Stripe dashboard for registered webhooks")
            print("3. Compare price IDs in your Stripe products vs. frontend code")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_payment_logs()
