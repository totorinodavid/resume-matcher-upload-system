#!/usr/bin/env python3
"""
🚨 SIMPLE STRIPE CHECK
Quick test to see if Stripe errors are resolved

USAGE: python simple_stripe_check.py
"""

import requests
import json
from datetime import datetime

def test_webhook():
    """Simple webhook test"""
    
    url = "https://resume-matcher-backend-j06k.onrender.com/"
    
    payload = {"test": "stripe_check", "time": str(datetime.now())}
    headers = {"Content-Type": "application/json"}
    
    print("🔄 Testing webhook endpoint...")
    print(f"📍 URL: {url}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.text[:300]}...")
        
        # Check for Stripe errors
        response_text = response.text
        
        if "Stripe module not available" in response_text:
            print("❌ RESULT: Stripe module still not available")
            return False
        elif "ImportError" in response_text and "stripe" in response_text.lower():
            print("❌ RESULT: Stripe import error still present")
            return False
        else:
            print("✅ RESULT: No Stripe import errors detected!")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚨 EMERGENCY STRIPE CHECK")
    print("=" * 50)
    
    success = test_webhook()
    
    if success:
        print("\n✅ SUCCESS: Emergency Stripe fix appears to be working!")
    else:
        print("\n❌ FAILURE: Stripe errors still present")
    
    print("=" * 50)
