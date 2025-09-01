#!/usr/bin/env python3
"""
Stripe Webhook Debugging Tool
============================

Creates a test webhook handler to see exactly what data arrives
and debug the user-ID mapping issue.
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"
FRONTEND_URL = "https://gojob.ing"

def test_user_id_mapping():
    """Test the user ID mapping and webhook processing logic"""
    print("🔍 STRIPE USER-ID MAPPING DEBUG")
    print("=" * 50)
    
    # Test 1: Check if webhook receives user_id in metadata
    print("📋 Testing Webhook Metadata Processing...")
    
    # Simulate a real Stripe checkout.session.completed event
    test_webhook = {
        "id": "evt_test_debug",
        "object": "event",
        "api_version": "2024-06-20",
        "created": int(datetime.now().timestamp()),
        "data": {
            "object": {
                "id": "cs_test_debug_session",
                "object": "checkout.session",
                "customer": None,  # First-time buyer has no customer ID
                "client_reference_id": "test_user_123",
                "metadata": {
                    "user_id": "test_user_123",  # This should be set by frontend
                    "credits": "100",
                    "price_id": "price_test_small",
                    "plan_id": "small"
                },
                "payment_status": "paid",
                "mode": "payment"
            }
        },
        "type": "checkout.session.completed"
    }
    
    print("🧪 Test webhook payload:")
    print(f"   User ID in metadata: {test_webhook['data']['object']['metadata']['user_id']}")
    print(f"   Credits in metadata: {test_webhook['data']['object']['metadata']['credits']}")
    print(f"   Customer ID: {test_webhook['data']['object']['customer']}")
    print()
    
    # Test 2: Send to webhook and see response
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/stripe/webhook",
            json=test_webhook,
            headers={
                "Stripe-Signature": "t=1693906800,v1=test_signature_for_debug",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        
        print(f"📡 Webhook Response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Webhook processed successfully: {data}")
                
                if data.get("skipped") == "no_user_mapping":
                    print("❌ PROBLEM FOUND: Webhook cannot resolve user_id!")
                    print("   The user_id from metadata is not being processed correctly")
                elif data.get("ok"):
                    print("✅ Webhook processing appears to work")
                    
            except:
                print("✅ Webhook processed (no JSON response)")
                
        elif response.status_code == 400:
            print("⚠️ Signature validation failed (expected in test)")
            print("   But this confirms webhook endpoint is reachable")
            
        elif response.status_code == 503:
            print("❌ PROBLEM: Webhook configuration missing!")
            print("   STRIPE_WEBHOOK_SECRET not configured")
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
    
    print()

def analyze_checkout_session_creation():
    """Analyze how checkout sessions are created and user IDs are set"""
    print("🔍 CHECKOUT SESSION CREATION ANALYSIS")
    print("=" * 50)
    
    # Test the checkout endpoint to see if it sets user_id correctly
    test_checkout_data = {
        "price_id": "price_test_small"
    }
    
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/stripe/checkout",
            json=test_checkout_data,
            timeout=15
        )
        
        print(f"📦 Checkout Response: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Checkout requires authentication (correct)")
            print("   This means user_id should be available during real purchases")
            
        elif response.status_code == 400:
            try:
                data = response.json()
                print(f"⚠️ Checkout error: {data}")
                
                if "price_id required" in str(data):
                    print("✅ Checkout endpoint is working (just needs valid price_id)")
                elif "Sign-in required" in str(data):
                    print("✅ Checkout properly checks for user authentication")
                    
            except:
                print("⚠️ Checkout returned 400 but no JSON")
                
        elif response.status_code == 200:
            try:
                data = response.json()
                print(f"⚠️ Unexpected successful checkout: {data}")
            except:
                print("⚠️ Checkout returned 200 but no JSON")
                
    except Exception as e:
        print(f"❌ Error testing checkout: {e}")
    
    print()

def check_stripe_customer_mapping():
    """Check if StripeCustomer mapping table is working"""
    print("🗃️ STRIPE CUSTOMER MAPPING TABLE CHECK")
    print("=" * 50)
    
    # The issue might be that the StripeCustomer table doesn't have entries
    # for first-time buyers, and the metadata fallback isn't working
    
    print("💡 POTENTIAL ISSUES:")
    print("1. First-time buyers don't have StripeCustomer table entries")
    print("2. Metadata user_id extraction is failing")
    print("3. User authentication state is lost between checkout and webhook")
    print("4. NextAuth user ID format doesn't match webhook expectations")
    print()
    
    print("🔧 DEBUGGING STEPS:")
    print("1. Check webhook logs during a real purchase")
    print("2. Verify user_id format in checkout session metadata")
    print("3. Ensure webhook can access user_id from metadata")
    print("4. Test StripeCustomer table creation for new users")
    print()

def run_comprehensive_user_id_debug():
    """Run complete user ID mapping diagnosis"""
    print("🚨 STRIPE USER-ID MAPPING DIAGNOSIS")
    print("=" * 60)
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_user_id_mapping()
    analyze_checkout_session_creation()
    check_stripe_customer_mapping()
    
    print("📊 LIKELY ROOT CAUSES:")
    print("=" * 40)
    print("1. 🔍 User ID not properly extracted from webhook metadata")
    print("2. 🗃️ StripeCustomer mapping table missing entries for first-time buyers")
    print("3. 🔐 Authentication context lost between checkout and webhook")
    print("4. 📝 Metadata user_id format mismatch")
    print()
    
    print("💡 NEXT DEBUGGING STEPS:")
    print("1. Monitor webhook logs during a real purchase")
    print("2. Check user_id in actual Stripe checkout session metadata")
    print("3. Verify _resolve_user_id function logic")
    print("4. Test StripeCustomer table operations")

if __name__ == "__main__":
    run_comprehensive_user_id_debug()
