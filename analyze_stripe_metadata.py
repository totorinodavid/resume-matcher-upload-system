#!/usr/bin/env python3
"""
Stripe Session Metadata Inspector
================================

Inspects the actual metadata structure in Stripe checkout sessions
to debug user ID mapping issues.
"""

import requests
import json
from datetime import datetime

FRONTEND_URL = "https://gojob.ing"
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

def analyze_checkout_metadata_structure():
    """Analyze how checkout sessions structure metadata"""
    print("🔍 STRIPE CHECKOUT METADATA ANALYSIS")
    print("=" * 50)
    
    # The key question: Does the checkout session ACTUALLY set user_id in metadata?
    print("📋 Checking Frontend Checkout Session Creation...")
    
    # Test with different authentication scenarios
    test_cases = [
        {
            "name": "Unauthenticated Request",
            "headers": {},
            "expected": "401 - Auth required"
        },
        {
            "name": "Test Authentication Header",
            "headers": {"x-e2e-user": "test_user_123"},
            "expected": "Should process if E2E_TEST_MODE enabled"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        try:
            response = requests.post(
                f"{FRONTEND_URL}/api/stripe/checkout",
                json={"price_id": "price_1234567890"},
                headers=test_case["headers"],
                timeout=15
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Expected: {test_case['expected']}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "url" in data:
                        print(f"   ✅ Checkout session created successfully!")
                        print(f"   Session URL: {data['url']}")
                        # This means metadata WAS set correctly
                    else:
                        print(f"   ⚠️ Unexpected success response: {data}")
                except:
                    print(f"   ⚠️ 200 response but no JSON")
                    
            elif response.status_code == 401:
                print(f"   ✅ Auth required (correct behavior)")
                
            elif response.status_code == 400:
                try:
                    data = response.json()
                    error_msg = data.get("error", "")
                    
                    if "price_id" in error_msg:
                        print(f"   ✅ Price validation working")
                    elif "Sign-in required" in error_msg:
                        print(f"   ✅ Auth validation working")
                    else:
                        print(f"   ⚠️ Different validation: {error_msg}")
                        
                except:
                    print(f"   ⚠️ 400 response but no JSON")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def test_metadata_extraction_logic():
    """Test the exact metadata extraction logic used by webhook"""
    print("\n🔧 METADATA EXTRACTION LOGIC TEST")
    print("=" * 45)
    
    # Simulate the exact structure that would come from Stripe
    test_stripe_objects = [
        {
            "name": "Typical First-Time Buyer",
            "stripe_obj": {
                "id": "cs_test_123",
                "customer": None,  # No customer ID for first-time buyers
                "metadata": {
                    "user_id": "user_abc123",
                    "credits": "100",
                    "price_id": "price_small"
                }
            }
        },
        {
            "name": "Empty Metadata",
            "stripe_obj": {
                "id": "cs_test_456",
                "customer": "cus_existing123",
                "metadata": {}
            }
        },
        {
            "name": "Null Metadata",
            "stripe_obj": {
                "id": "cs_test_789",
                "customer": None,
                "metadata": None
            }
        }
    ]
    
    for test in test_stripe_objects:
        print(f"\n🧪 Test: {test['name']}")
        obj = test['stripe_obj']
        
        # Simulate webhook _resolve_user_id logic
        stripe_customer_id = obj.get("customer")
        meta = obj.get("metadata") or {}
        
        print(f"   Stripe Customer ID: {stripe_customer_id}")
        print(f"   Metadata: {meta}")
        
        # Simulate the exact logic from webhooks.py
        if stripe_customer_id:
            print(f"   → Would lookup customer in StripeCustomer table")
        
        # Metadata fallback
        user_id = meta.get("user_id") if isinstance(meta, dict) else None
        print(f"   → Extracted user_id from metadata: {user_id}")
        
        if user_id:
            print(f"   ✅ User ID resolution would SUCCEED")
        else:
            print(f"   ❌ User ID resolution would FAIL → 'no_user_mapping'")

def identify_likely_root_cause():
    """Identify the most likely root cause based on analysis"""
    print("\n🎯 ROOT CAUSE ANALYSIS")
    print("=" * 30)
    
    print("Based on the code analysis, the most likely issues are:")
    print()
    print("1. 🔐 AUTHENTICATION CONTEXT LOSS")
    print("   → User is not signed in during checkout")
    print("   → NextAuth session is invalid/expired")
    print("   → user_id is not being set in metadata")
    print()
    print("2. 📝 USER ID FORMAT MISMATCH")
    print("   → NextAuth user ID format doesn't match expectations")
    print("   → Special characters or encoding in user_id")
    print("   → Empty or null user_id in session")
    print()
    print("3. 🗃️ STRIPE CUSTOMER MAPPING")
    print("   → First-time buyers don't have StripeCustomer entries")
    print("   → StripeCustomer table lookup fails")
    print("   → Fallback to metadata doesn't work")
    print()
    print("💡 DEBUGGING RECOMMENDATION:")
    print("1. Check if user is ACTUALLY signed in during purchase")
    print("2. Verify NextAuth session contains valid user_id")
    print("3. Test checkout with a known good user session")
    print("4. Monitor webhook logs during real purchase")

def run_metadata_analysis():
    """Run complete metadata analysis"""
    print("🚨 STRIPE METADATA & USER-ID ANALYSIS")
    print("=" * 60)
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    analyze_checkout_metadata_structure()
    test_metadata_extraction_logic()
    identify_likely_root_cause()
    
    print()
    print("🎯 IMMEDIATE ACTION REQUIRED:")
    print("1. Test a purchase while SIGNED IN")
    print("2. Verify your NextAuth session is valid")
    print("3. Check browser dev tools for user authentication")
    print("4. Monitor webhook responses during real purchase")

if __name__ == "__main__":
    run_metadata_analysis()
