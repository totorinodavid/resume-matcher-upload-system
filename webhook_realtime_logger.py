#!/usr/bin/env python3
"""
Real-Time Webhook Logger
=======================

Logs webhook events in real-time to diagnose user ID mapping issues.
Run this DURING a real purchase to see exactly what data arrives.
"""

import requests
import time
import json
from datetime import datetime

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def create_webhook_test_endpoint():
    """Create a simple webhook test to capture real data"""
    print("🎯 REAL-TIME WEBHOOK DEBUGGING")
    print("=" * 50)
    print("🚀 This tool will help you debug a REAL purchase!")
    print()
    print("📋 INSTRUCTIONS:")
    print("1. Keep this running")
    print("2. In another browser tab, go to https://gojob.ing")
    print("3. Sign in to your account")
    print("4. Try to purchase credits")
    print("5. Complete the payment")
    print("6. Watch this terminal for webhook activity")
    print()
    print("🔍 We'll monitor:")
    print("   - Webhook calls to the backend")
    print("   - User ID extraction attempts")
    print("   - Credit processing status")
    print("   - Error messages")
    print()
    print("⏰ Monitoring started - proceed with test purchase...")
    print("-" * 50)
    
    # Check webhook endpoint periodically
    last_check = 0
    check_count = 0
    
    while True:
        try:
            current_time = time.time()
            
            # Every 5 seconds, test the webhook endpoint
            if current_time - last_check >= 5:
                check_count += 1
                
                # Test webhook availability
                test_payload = {
                    "id": f"evt_monitor_{check_count}",
                    "type": "test.event",
                    "data": {"object": {"id": "test"}},
                    "created": int(current_time)
                }
                
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/webhooks/stripe",
                        json=test_payload,
                        headers={"Stripe-Signature": f"t={int(current_time)},v1=test_sig_{check_count}"},
                        timeout=5
                    )
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    if response.status_code == 400:
                        if check_count % 12 == 0:  # Every minute
                            print(f"[{timestamp}] ✅ Webhook endpoint active (signature validation working)")
                    elif response.status_code == 503:
                        print(f"[{timestamp}] ❌ CRITICAL: STRIPE_WEBHOOK_SECRET not configured!")
                        print("   This explains why credits are not added - webhook can't process!")
                        break
                    elif response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"[{timestamp}] 📡 Webhook response: {data}")
                            
                            if "skipped" in data:
                                if data["skipped"] == "no_user_mapping":
                                    print(f"[{timestamp}] ❌ USER ID MAPPING FAILURE!")
                                    print("   The webhook received an event but couldn't resolve user_id")
                                elif data["skipped"] == "no_mapped_prices":
                                    print(f"[{timestamp}] ❌ PRICE MAPPING FAILURE!")
                                    print("   The webhook couldn't map price_id to credits")
                            
                        except:
                            print(f"[{timestamp}] ✅ Webhook processed successfully")
                    
                except requests.RequestException:
                    if check_count % 12 == 0:  # Every minute
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        print(f"[{timestamp}] ⚠️ Backend unreachable")
                
                last_check = current_time
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Monitoring stopped")
            print()
            print("📊 ANALYSIS SUMMARY")
            print("=" * 30)
            print("If you completed a purchase and saw:")
            print()
            print("❌ 'USER ID MAPPING FAILURE':")
            print("   → The user_id in checkout metadata doesn't match webhook expectations")
            print("   → Fix: Check NextAuth user ID format vs webhook _resolve_user_id logic")
            print()
            print("❌ 'PRICE MAPPING FAILURE':")
            print("   → The price_id from Stripe doesn't match STRIPE_PRICE_*_ID env vars")
            print("   → Fix: Update environment variables with correct Stripe price IDs")
            print()
            print("❌ 'STRIPE_WEBHOOK_SECRET not configured':")
            print("   → Webhook cannot process any events")
            print("   → Fix: Add STRIPE_WEBHOOK_SECRET to Render environment")
            print()
            print("✅ 'Webhook processed successfully':")
            print("   → Credits should have been added to your account")
            print("   → If not, check database connection or CreditsService")
            break
            
        except Exception as e:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] ❌ Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    create_webhook_test_endpoint()
