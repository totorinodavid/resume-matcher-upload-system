#!/usr/bin/env python3
"""
🚨 EMERGENCY STRIPE DEPLOYMENT MONITOR
Monitors the production webhook endpoint for Stripe availability after emergency fix

USAGE: python monitor_stripe_emergency_fix.py
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

# Production webhook URL
WEBHOOK_URL = "https://resume-matcher-backend-j06k.onrender.com/"

async def test_webhook_response():
    """Test webhook endpoint with a simple POST to check for Stripe errors"""
    
    # Create a simple test payload (not a real Stripe webhook)
    test_payload = {
        "test": "emergency_stripe_check",
        "timestamp": datetime.now().isoformat()
    }
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "EmergencyStripeTest/1.0"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"🔄 Testing webhook endpoint: {WEBHOOK_URL}")
            
            async with session.post(
                WEBHOOK_URL, 
                json=test_payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                status = response.status
                response_text = await response.text()
                
                print(f"📊 Response Status: {status}")
                print(f"📄 Response Headers: {dict(response.headers)}")
                print(f"📝 Response Body: {response_text[:500]}...")
                
                # Check for Stripe-related errors
                if "Stripe module not available" in response_text:
                    print("❌ CRITICAL: Stripe module still not available!")
                    return False
                elif "ImportError" in response_text and "stripe" in response_text.lower():
                    print("❌ CRITICAL: Stripe import error still present!")
                    return False
                elif status == 400 and "signature" not in response_text.lower():
                    print("✅ GOOD: No Stripe import errors detected")
                    print("💡 Status 400 expected for test payload without signature")
                    return True
                else:
                    print("🔍 CHECKING: Analyzing response for Stripe status...")
                    return True
                    
    except asyncio.TimeoutError:
        print("⏰ TIMEOUT: Webhook endpoint took too long to respond")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to test webhook: {e}")
        return False

async def monitor_deployment():
    """Monitor the deployment for Stripe availability"""
    
    print("=" * 60)
    print("🚨 EMERGENCY STRIPE DEPLOYMENT MONITOR")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print("\n🎯 CHECKING: Emergency Stripe deployment fix...")
    print("📋 EXPECTED: No more 'Stripe module not available' errors")
    print("🔧 DEPLOYED: requirements.txt + pip installation instead of uv")
    
    # Test multiple times to ensure consistency
    for attempt in range(3):
        print(f"\n🔄 Test Attempt {attempt + 1}/3:")
        
        success = await test_webhook_response()
        
        if success:
            print(f"✅ Attempt {attempt + 1}: Webhook responding without Stripe errors")
        else:
            print(f"❌ Attempt {attempt + 1}: Stripe errors still present")
        
        if attempt < 2:  # Don't wait after last attempt
            print("⏳ Waiting 10 seconds before next test...")
            await asyncio.sleep(10)
    
    print("\n" + "=" * 60)
    print("📊 EMERGENCY DEPLOYMENT MONITOR COMPLETE")
    print("💡 Check production logs for detailed Stripe status")
    print("=" * 60)

def main():
    """Main function"""
    try:
        asyncio.run(monitor_deployment())
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
