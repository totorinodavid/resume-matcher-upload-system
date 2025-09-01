#!/usr/bin/env python3
"""
Quick Authentication & User ID Test
==================================

Simple test to verify if user authentication is working
during the checkout process.
"""

import requests

def test_user_authentication():
    """Test if user authentication is working properly"""
    print("🔐 USER AUTHENTICATION TEST")
    print("=" * 40)
    print()
    print("This test will check if the authentication system")
    print("is working correctly for the checkout process.")
    print()
    
    # Test current user endpoint
    try:
        response = requests.get("https://gojob.ing/api/auth/session", timeout=10)
        print(f"Session endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("user"):
                    print("✅ User session found!")
                    print(f"   User ID: {data['user'].get('id', 'NOT_FOUND')}")
                    print(f"   Email: {data['user'].get('email', 'NOT_FOUND')}")
                else:
                    print("❌ No user in session")
            except:
                print("⚠️ Session response not JSON")
        else:
            print("❌ Session endpoint not accessible")
            
    except Exception as e:
        print(f"❌ Session test failed: {e}")
    
    print()
    print("🛒 CHECKOUT AUTHENTICATION TEST")
    print("=" * 40)
    
    # Test checkout endpoint
    try:
        response = requests.post(
            "https://gojob.ing/api/stripe/checkout",
            json={"price_id": "price_test"},
            timeout=10
        )
        
        print(f"Checkout endpoint status: {response.status_code}")
        
        if response.status_code == 401:
            try:
                data = response.json()
                error_msg = data.get("error", "")
                
                if "Sign-in required" in error_msg:
                    print("✅ Checkout properly requires authentication")
                    print("   This means user_id SHOULD be available when signed in")
                else:
                    print(f"⚠️ Different auth error: {error_msg}")
                    
            except:
                print("✅ Checkout requires authentication (no JSON)")
                
        elif response.status_code == 400:
            print("⚠️ Checkout accepted request - possible auth bypass")
            
        elif response.status_code == 200:
            print("❌ Checkout worked without authentication - PROBLEM!")
            
    except Exception as e:
        print(f"❌ Checkout test failed: {e}")
    
    print()
    print("🎯 DIAGNOSIS:")
    print("=" * 20)
    print("If checkout shows 'Sign-in required', then:")
    print("1. ✅ Authentication is working correctly")
    print("2. 🔍 The issue is likely in the webhook user_id extraction")
    print("3. 💡 User might not be properly signed in during actual purchase")
    print()
    print("If checkout works without authentication:")
    print("1. ❌ Authentication bypass - security issue")
    print("2. 🔧 Need to fix authentication requirements")
    print()
    print("Next step: TEST A REAL PURCHASE while properly signed in!")

if __name__ == "__main__":
    test_user_authentication()
