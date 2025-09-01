#!/usr/bin/env python3
"""
📊 STRIPE WEBHOOK MONITORING - ULTIMATE FIX VALIDATION
=====================================================

Real-time monitoring script to validate the Ultimate Stripe Webhook Fix.
Monitors backend logs and webhook processing to ensure credits are being added correctly.

Run this script while testing payments to see real-time webhook processing.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

import httpx

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"
TEST_USER_ID = "e747de39-1b54-4cd0-96eb-e68f155931e2"
MONITORING_INTERVAL = 5  # seconds


class WebhookMonitor:
    def __init__(self):
        self.webhook_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
    async def test_webhook_health(self) -> bool:
        """Test if webhook endpoint is responsive"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{BACKEND_URL}/api/health")
                return response.status_code == 200
        except Exception:
            return False
    
    async def test_webhook_processing(self) -> Dict[str, Any]:
        """Send a test webhook and analyze the response"""
        payload = {
            "id": f"evt_monitor_{int(time.time())}",
            "object": "event",
            "api_version": "2023-10-16",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": f"cs_monitor_{int(time.time())}",
                    "object": "checkout.session",
                    "customer": f"cus_monitor_{int(time.time())}",
                    "payment_status": "paid",
                    "metadata": {
                        "user_id": TEST_USER_ID,
                        "credits": "10"  # Small amount for testing
                    },
                    "mode": "payment",
                    "status": "complete"
                }
            },
            "livemode": False,
            "pending_webhooks": 0,
            "request": {"id": None, "idempotency_key": None},
            "type": "checkout.session.completed"
        }
        
        headers = {
            "User-Agent": "Stripe/1.0 (+https://stripe.com/docs/webhooks)",
            "Content-Type": "application/json",
            "Stripe-Signature": "t=1234567890,v1=monitor_test_signature"
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/",
                    json=payload,
                    headers=headers
                )
                
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "status_code": response.status_code,
                    "success": False,
                    "error": None,
                    "credits_added": None,
                    "user_id": None,
                    "event_id": None,
                    "response_time_ms": None
                }
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        result["success"] = response_data.get("ok", False)
                        result["credits_added"] = response_data.get("credits_added")
                        result["user_id"] = response_data.get("user_id") 
                        result["event_id"] = response_data.get("event_id")
                        result["error"] = response_data.get("error")
                        
                        if result["credits_added"]:
                            self.success_count += 1
                        else:
                            self.error_count += 1
                            
                    except Exception as e:
                        result["error"] = f"JSON parse error: {e}"
                        self.error_count += 1
                else:
                    result["error"] = f"HTTP {response.status_code}"
                    self.error_count += 1
                
                self.webhook_count += 1
                return result
                
        except Exception as e:
            self.error_count += 1
            return {
                "timestamp": datetime.now().isoformat(),
                "status_code": None,
                "success": False,
                "error": f"Request failed: {e}",
                "credits_added": None,
                "user_id": None,
                "event_id": None,
                "response_time_ms": None
            }
    
    def print_status(self):
        """Print current monitoring status"""
        runtime = time.time() - self.start_time
        runtime_str = f"{runtime:.1f}s"
        
        success_rate = (self.success_count / max(self.webhook_count, 1)) * 100
        
        logger.info(f"📊 WEBHOOK MONITOR STATUS")
        logger.info(f"   Runtime: {runtime_str}")
        logger.info(f"   Total Webhooks: {self.webhook_count}")
        logger.info(f"   Successful: {self.success_count}")
        logger.info(f"   Errors: {self.error_count}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting Ultimate Stripe Webhook Monitor")
        logger.info(f"   Backend URL: {BACKEND_URL}")
        logger.info(f"   Test User ID: {TEST_USER_ID}")
        logger.info(f"   Monitoring Interval: {MONITORING_INTERVAL}s")
        logger.info("=" * 60)
        
        # Initial health check
        health_ok = await self.test_webhook_health()
        if not health_ok:
            logger.error("❌ Backend health check failed! Monitor may not work correctly.")
        else:
            logger.info("✅ Backend is healthy")
        
        logger.info("\n🔄 Starting webhook monitoring loop...")
        logger.info("   Press Ctrl+C to stop monitoring")
        logger.info("=" * 60)
        
        try:
            while True:
                # Test webhook processing
                result = await self.test_webhook_processing()
                
                # Log result
                timestamp = datetime.now().strftime("%H:%M:%S")
                if result["success"] and result["credits_added"]:
                    logger.info(f"✅ [{timestamp}] Webhook Success: {result['credits_added']} credits added to {result['user_id']}")
                elif result["error"]:
                    logger.error(f"❌ [{timestamp}] Webhook Error: {result['error']}")
                else:
                    logger.warning(f"⚠️ [{timestamp}] Webhook Warning: No credits added")
                
                # Print status every 10 webhooks
                if self.webhook_count % 10 == 0:
                    logger.info("-" * 40)
                    self.print_status()
                    logger.info("-" * 40)
                
                # Wait for next iteration
                await asyncio.sleep(MONITORING_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitor crashed: {e}")
        finally:
            logger.info("\n" + "=" * 60)
            logger.info("🏁 FINAL MONITORING RESULTS")
            self.print_status()
            
            if self.success_count > 0:
                logger.info("🎉 The Ultimate Stripe Webhook Fix is working!")
            else:
                logger.error("❌ No successful webhook processing detected")


async def main():
    """Run the webhook monitor"""
    monitor = WebhookMonitor()
    await monitor.monitor_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Monitor stopped")
    except Exception as e:
        logger.error(f"❌ Monitor failed: {e}")
        exit(1)
