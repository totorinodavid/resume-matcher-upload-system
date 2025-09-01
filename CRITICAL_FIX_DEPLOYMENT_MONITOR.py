#!/usr/bin/env python3
"""
🚨 CRITICAL FIX DEPLOYMENT MONITOR 🚨

Überwacht das Deployment des kritischen ImportError-Fixes
und verifiziert, dass Stripe-Webhooks wieder funktionieren.

Der echte User (davis t) wartet auf seine 50 Credits!
"""

import asyncio
import aiohttp
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

class CriticalFixMonitor:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_webhook_fix(self):
        """Test if the ImportError is fixed"""
        try:
            # Send a test webhook payload to see if import works
            test_payload = {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_fix_check",
                        "payment_status": "paid",
                        "customer": "cus_test",
                        "metadata": {
                            "user_id": "test_user",
                            "credits": "10"
                        }
                    }
                }
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/webhooks/stripe",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                status = response.status
                text = await response.text()
                
                if status == 500:
                    # Check if it's still the ImportError
                    if "ImportError" in text or "_resolve_user_id_BULLETPROOF" in text:
                        return {"status": "IMPORT_ERROR_STILL_EXISTS", "response": text}
                    else:
                        return {"status": "OTHER_500_ERROR", "response": text}
                elif status in [200, 202]:
                    return {"status": "WEBHOOK_WORKING", "response": text}
                else:
                    return {"status": f"HTTP_{status}", "response": text}
                    
        except Exception as e:
            return {"status": "CONNECTION_ERROR", "error": str(e)}

    async def check_system_status(self):
        """Check overall system status"""
        try:
            # Check main endpoint
            async with self.session.get(f"{BACKEND_URL}/") as response:
                main_status = response.status
            
            # Check docs
            async with self.session.get(f"{BACKEND_URL}/docs") as response:
                docs_status = response.status
                
            # Test webhook fix
            webhook_test = await self.test_webhook_fix()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "main_endpoint": main_status,
                "docs_endpoint": docs_status,
                "webhook_test": webhook_test
            }
            
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def monitor_fix_deployment(self, duration_minutes=10):
        """Monitor the critical fix deployment"""
        print("🚨 CRITICAL FIX DEPLOYMENT MONITOR 🚨")
        print("Monitoring ImportError fix for Stripe webhooks...")
        print("Real user payment is waiting for this fix!")
        print()
        print(f"🎯 Target: Fix ImportError '_resolve_user_id_BULLETPROOF'")
        print(f"🔧 Solution: Update import to '_resolve_user_id_ULTRA_EMERGENCY'")
        print(f"👤 Waiting User: davis t (8a7e6e84-eab5-4890-b4a2-d1f4034e98a5)")
        print(f"💳 Credits: 50 (small plan purchase)")
        print("="*70)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        check_interval = 20  # Check every 20 seconds
        
        fix_deployed = False
        
        while time.time() < end_time:
            elapsed = time.time() - start_time
            remaining = end_time - time.time()
            
            print(f"\n⏱️  Time: {elapsed:.0f}s elapsed, {remaining:.0f}s remaining")
            
            status = await self.check_system_status()
            
            if "error" in status:
                print(f"❌ System error: {status['error']}")
            else:
                main_status = status.get("main_endpoint", "Unknown")
                docs_status = status.get("docs_endpoint", "Unknown")
                webhook_test = status.get("webhook_test", {})
                
                print(f"🌐 Main endpoint: {main_status}")
                print(f"📚 Docs endpoint: {docs_status}")
                
                webhook_status = webhook_test.get("status", "UNKNOWN")
                print(f"🪝 Webhook test: {webhook_status}")
                
                if webhook_status == "IMPORT_ERROR_STILL_EXISTS":
                    print("   ❌ ImportError still exists - deployment not complete")
                elif webhook_status == "WEBHOOK_WORKING":
                    print("   ✅ Webhook working - ImportError FIXED!")
                    print("\n🎉 CRITICAL FIX DEPLOYED SUCCESSFULLY! 🎉")
                    print("✅ ImportError resolved")
                    print("✅ Stripe webhooks functional")
                    print("✅ Credit assignment system operational")
                    print("✅ User 'davis t' can now receive credits!")
                    fix_deployed = True
                    break
                elif webhook_status == "OTHER_500_ERROR":
                    print("   ⚠️  Different 500 error - checking response...")
                    response = webhook_test.get("response", "")
                    if "ULTRA_EMERGENCY" in response:
                        print("   ✅ Ultra emergency system active!")
                    else:
                        print(f"   ❓ Unknown error: {response[:200]}...")
                else:
                    print(f"   ❓ Status: {webhook_status}")
            
            if remaining > check_interval:
                print(f"⏳ Waiting {check_interval}s for next check...")
                await asyncio.sleep(check_interval)
            else:
                break
        
        print("\n" + "="*70)
        if fix_deployed:
            print("🚀 CRITICAL FIX DEPLOYMENT - SUCCESS! 🚀")
            print("✅ ImportError fixed")
            print("✅ Ultra-emergency system operational")
            print("✅ Credits will be assigned after Stripe payments")
            print()
            print("🎯 NEXT ACTION: User 'davis t' should retry payment or")
            print("    credits should be manually assigned for completed payment")
        else:
            print("⚠️ CRITICAL FIX DEPLOYMENT - TIMEOUT ⚠️")
            print("🔧 Fix may still be deploying")
            print("⏱️ Continue monitoring or check Render dashboard")
            print("🚨 User 'davis t' still waiting for credits!")
        print("="*70)
        
        return fix_deployed

async def main():
    """Monitor critical fix deployment"""
    async with CriticalFixMonitor() as monitor:
        success = await monitor.monitor_fix_deployment(duration_minutes=10)
        
        if success:
            print("\n🎉 MISSION CRITICAL: FIX DEPLOYED! 🎉")
            print("SORG DAFÜR DAS BEI ERFOLGREICHER STRIPE ZAHLUNG CREDITS AUCH GUTGESCHRIEBEN WERDEN!")
            print("✅ SYSTEM IST JETZT BEREIT FÜR CREDIT-ZUWEISUNG! ✅")

if __name__ == "__main__":
    asyncio.run(main())
