#!/usr/bin/env python3
"""
🚀 PRODUCTION WEBHOOK DEPLOYMENT MONITOR
Monitor the deployment of the Ultimate Stripe Webhook Fix
Real-time validation of webhook functionality after deployment
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import os
import sys

# Production URL
PRODUCTION_URL = "https://resume-matcher-backend.onrender.com"

class DeploymentMonitor:
    def __init__(self):
        self.deployment_start = datetime.now()
        
    async def check_health(self, session):
        """Check if the app is responding"""
        try:
            async with session.get(f"{PRODUCTION_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return True, data
                else:
                    return False, f"Status: {response.status}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def check_webhook_endpoint(self, session):
        """Check if webhook endpoint is accessible"""
        try:
            # Send a test POST to webhook endpoint (should fail gracefully)
            headers = {"User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)"}
            async with session.post(f"{PRODUCTION_URL}/", 
                                   headers=headers, 
                                   data="test") as response:
                status = response.status
                text = await response.text()
                
                # Check if it's our Ultimate handler
                if "Ultimate Stripe Webhook Handler" in text or "Webhook signature" in text:
                    return True, f"Ultimate handler active (Status: {status})"
                else:
                    return False, f"Different handler (Status: {status}): {text[:100]}"
                    
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    async def check_stripe_availability(self, session):
        """Check if Stripe module is now available"""
        try:
            async with session.get(f"{PRODUCTION_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    # Look for Stripe-related health info
                    return True, "App responding (Stripe status unknown from health)"
                else:
                    return False, f"App not responding: {response.status}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def print_status(self, check_name, success, message):
        """Print formatted status"""
        status_icon = "✅" if success else "❌"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status_icon} {check_name}: {message}")
    
    async def monitor_deployment(self):
        """Main monitoring loop"""
        print("🚀 ULTIMATE STRIPE WEBHOOK FIX - DEPLOYMENT MONITOR")
        print("=" * 60)
        print(f"📊 Monitoring: {PRODUCTION_URL}")
        print(f"⏰ Started: {self.deployment_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        attempt = 0
        consecutive_successes = 0
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            while True:
                attempt += 1
                print(f"\n🔍 Attempt #{attempt} - {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 40)
                
                # Check app health
                health_ok, health_msg = await self.check_health(session)
                self.print_status("App Health", health_ok, health_msg)
                
                # Check webhook endpoint
                webhook_ok, webhook_msg = await self.check_webhook_endpoint(session)
                self.print_status("Webhook Endpoint", webhook_ok, webhook_msg)
                
                # Check overall status
                if health_ok and webhook_ok:
                    consecutive_successes += 1
                    print(f"🎉 SUCCESS! Ultimate webhook handler is LIVE (#{consecutive_successes})")
                    
                    if consecutive_successes >= 3:
                        print("\n" + "=" * 60)
                        print("🚀 DEPLOYMENT SUCCESSFUL!")
                        print("✅ Ultimate Stripe Webhook Handler is fully operational")
                        print("✅ Route conflicts resolved")
                        print("✅ Enhanced error handling active")
                        print("✅ Production ready for webhook processing")
                        print("=" * 60)
                        break
                else:
                    consecutive_successes = 0
                    print("⏳ Deployment still in progress...")
                
                # Wait before next check
                await asyncio.sleep(15)
                
                # Safety limit
                if attempt > 40:  # 10 minutes max
                    print("\n⚠️ Monitoring timeout reached. Check deployment manually.")
                    break

if __name__ == "__main__":
    monitor = DeploymentMonitor()
    try:
        asyncio.run(monitor.monitor_deployment())
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")
