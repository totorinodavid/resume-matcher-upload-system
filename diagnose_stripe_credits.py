#!/usr/bin/env python3
"""
Stripe Credits Debugging Tool
============================

Diagnoses why Stripe payments are successful but credits are not added.
Tests webhook configuration, credit system, and end-to-end flow.
"""

import requests
import json
from datetime import datetime

# Production URLs
FRONTEND_URL = "https://gojob.ing"
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def test_backend_config():
    """Test if backend has required Stripe configuration"""
    print("🔧 Testing Backend Stripe Configuration...")
    
    try:
        # Test if backend has stripe configured
        response = requests.get(f"{BACKEND_URL}/healthz", timeout=10)
        
        if response.status_code == 200:
            print("  ✅ Backend is healthy")
        else:
            print(f"  ❌ Backend unhealthy: {response.status_code}")
            return
        
        # Test webhook endpoint availability
        response = requests.post(
            f"{BACKEND_URL}/webhooks/stripe",
            json={"test": "ping"},
            headers={"Stripe-Signature": "test"},
            timeout=10
        )
        
        if response.status_code == 503:
            print("  ❌ PROBLEM: Stripe webhook not configured (STRIPE_WEBHOOK_SECRET missing)")
        elif response.status_code == 400:
            print("  ✅ Webhook endpoint exists (signature validation working)")
        else:
            print(f"  ⚠️ Unexpected webhook response: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error testing backend config: {e}")

def test_credit_system():
    """Test if credit system is working"""
    print("💳 Testing Credit System...")
    
    try:
        # Test credits endpoint (should require auth)
        response = requests.get(f"{BACKEND_URL}/api/v1/me/credits", timeout=10)
        
        if response.status_code == 401:
            print("  ✅ Credits endpoint exists (auth required)")
        elif response.status_code == 200:
            data = response.json()
            print(f"  ✅ Credits endpoint working: {data}")
        else:
            print(f"  ⚠️ Unexpected credits response: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error testing credits: {e}")

def test_stripe_webhook_delivery():
    """Test webhook delivery path"""
    print("🔗 Testing Stripe Webhook Delivery Path...")
    
    try:
        # Test frontend webhook proxy
        response = requests.post(
            f"{FRONTEND_URL}/api/stripe/webhook",
            json={"test": "frontend_webhook"},
            headers={"Stripe-Signature": "test_sig"},
            timeout=15
        )
        
        if response.status_code == 503:
            print("  ❌ CRITICAL: Backend webhook not configured!")
            print("     Missing STRIPE_WEBHOOK_SECRET in production environment")
        elif response.status_code == 400:
            print("  ✅ Webhook proxy working (signature validation active)")
        else:
            print(f"  ⚠️ Webhook proxy response: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error testing webhook delivery: {e}")

def analyze_stripe_configuration():
    """Analyze what Stripe configuration is missing"""
    print("📊 Stripe Configuration Analysis...")
    
    issues = []
    
    # Check webhook secret
    try:
        response = requests.post(
            f"{BACKEND_URL}/webhooks/stripe",
            json={"type": "test"},
            headers={"Stripe-Signature": "test"},
            timeout=10
        )
        
        if response.status_code == 503:
            issues.append("❌ STRIPE_WEBHOOK_SECRET not configured in production")
        
    except Exception:
        pass
    
    if issues:
        print("  🚨 CRITICAL ISSUES FOUND:")
        for issue in issues:
            print(f"    {issue}")
        
        print("\n  💡 REQUIRED ACTIONS:")
        print("    1. Configure STRIPE_WEBHOOK_SECRET in Render environment")
        print("    2. Configure STRIPE_PRICE_*_ID variables")
        print("    3. Register webhook endpoint with Stripe")
        print("    4. Test webhook delivery")
    else:
        print("  ✅ Basic webhook configuration appears correct")

def simulate_webhook_test():
    """Simulate a webhook test to see what happens"""
    print("🧪 Simulating Webhook Test...")
    
    # This is what a real Stripe webhook looks like
    test_webhook = {
        "id": "evt_test_webhook",
        "object": "event",
        "api_version": "2024-06-20",
        "created": 1693906800,
        "data": {
            "object": {
                "id": "cs_test_session",
                "object": "checkout.session",
                "customer": "cus_test_customer",
                "metadata": {
                    "user_id": "test_user_123",
                    "credits": "100",
                    "price_id": "price_test_small"
                },
                "payment_status": "paid"
            }
        },
        "type": "checkout.session.completed"
    }
    
    try:
        response = requests.post(
            f"{FRONTEND_URL}/api/stripe/webhook",
            json=test_webhook,
            headers={
                "Stripe-Signature": "t=1693906800,v1=test_signature",
                "Content-Type": "application/json"
            },
            timeout=15
        )
        
        print(f"  Test webhook response: {response.status_code}")
        
        if response.status_code == 503:
            print("  ❌ Webhook configuration missing - credits cannot be processed!")
        elif response.status_code == 400:
            print("  ⚠️ Signature validation failed (expected in test)")
        elif response.status_code == 200:
            print("  ✅ Webhook processed successfully")
            try:
                data = response.json()
                print(f"  Response: {data}")
            except:
                pass
        
    except Exception as e:
        print(f"  ❌ Error testing webhook: {e}")

def run_credits_diagnosis():
    """Run complete diagnosis of credits issue"""
    print("🔍 STRIPE CREDITS DIAGNOSIS")
    print("=" * 50)
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_backend_config()
    print()
    
    test_credit_system()
    print()
    
    test_stripe_webhook_delivery()
    print()
    
    analyze_stripe_configuration()
    print()
    
    simulate_webhook_test()
    print()
    
    print("📋 SUMMARY")
    print("=" * 30)
    print("If you see 'STRIPE_WEBHOOK_SECRET not configured':")
    print("1. 🔧 Add STRIPE_WEBHOOK_SECRET to Render environment variables")
    print("2. 🔧 Add STRIPE_PRICE_*_ID variables for your products")
    print("3. 🔗 Register webhook URL with Stripe: https://gojob.ing/api/stripe/webhook")
    print("4. 🧪 Test a real purchase to verify credits are added")
    print()
    print("The payment succeeds but credits fail because webhook cannot process!")

if __name__ == "__main__":
    run_credits_diagnosis()
