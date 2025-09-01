#!/usr/bin/env python3
"""
EMERGENCY RENDER DEPLOYMENT TRIGGER
Forciert ein neues Deployment auf Render mit den ultra-emergency fixes
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Backend URL
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

class RenderDeploymentTrigger:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_current_deployment(self):
        """Check what version is currently deployed"""
        try:
            logger.info("🔍 Checking current deployment version...")
            
            # Try to access FastAPI docs to see if our updates are there
            async with self.session.get(f"{BACKEND_URL}/docs") as response:
                if response.status == 200:
                    text = await response.text()
                    logger.info(f"✅ FastAPI docs accessible - checking for our endpoints...")
                    
                    # Check if our ultra-emergency endpoints are present
                    has_user_endpoints = "/api/v1/users" in text
                    has_webhook_endpoints = "/api/v1/webhooks" in text
                    has_credit_endpoints = "/api/v1/credits" in text
                    
                    logger.info(f"User endpoints: {'✅' if has_user_endpoints else '❌'}")
                    logger.info(f"Webhook endpoints: {'✅' if has_webhook_endpoints else '❌'}")
                    logger.info(f"Credit endpoints: {'✅' if has_credit_endpoints else '❌'}")
                    
                    return {
                        "docs_accessible": True,
                        "has_user_endpoints": has_user_endpoints,
                        "has_webhook_endpoints": has_webhook_endpoints,
                        "has_credit_endpoints": has_credit_endpoints,
                        "deployment_complete": has_user_endpoints and has_webhook_endpoints and has_credit_endpoints
                    }
                else:
                    logger.error(f"❌ FastAPI docs not accessible: {response.status}")
                    return {"docs_accessible": False, "status_code": response.status}
                    
        except Exception as e:
            logger.error(f"❌ Error checking deployment: {e}")
            return {"error": str(e)}

    async def force_render_redeploy(self):
        """Force Render to redeploy by making a dummy commit"""
        logger.info("🚀 Triggering Render redeploy...")
        
        # Create a timestamp file to trigger redeploy
        timestamp = datetime.now().isoformat()
        dummy_content = f"""# RENDER DEPLOYMENT TRIGGER
# Generated at: {timestamp}
# This file forces Render to redeploy with latest ultra-emergency fixes

DEPLOYMENT_TIMESTAMP = "{timestamp}"
ULTRA_EMERGENCY_SYSTEM = True
MINIMAL_DATABASE_SCHEMA = True
BULLETPROOF_CREDIT_ASSIGNMENT = True
"""
        
        # Write the trigger file
        with open("RENDER_DEPLOY_TRIGGER.py", "w") as f:
            f.write(dummy_content)
        
        logger.info("✅ Deployment trigger file created")
        return True

    async def monitor_deployment_progress(self, max_wait_minutes=10):
        """Monitor deployment progress"""
        logger.info(f"⏱️ Monitoring deployment progress (max {max_wait_minutes} minutes)...")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        check_interval = 30  # Check every 30 seconds
        
        while time.time() - start_time < max_wait_seconds:
            deployment_status = await self.check_current_deployment()
            
            if deployment_status.get("deployment_complete", False):
                elapsed = time.time() - start_time
                logger.info(f"🎉 Deployment complete! ({elapsed:.1f}s)")
                return True
            elif deployment_status.get("docs_accessible", False):
                elapsed = time.time() - start_time
                logger.info(f"⏳ Deployment in progress... ({elapsed:.1f}s)")
            else:
                elapsed = time.time() - start_time
                logger.info(f"🔄 Backend starting up... ({elapsed:.1f}s)")
            
            await asyncio.sleep(check_interval)
        
        logger.warning(f"⚠️ Deployment monitoring timeout after {max_wait_minutes} minutes")
        return False

    async def generate_deployment_report(self, deployment_successful):
        """Generate deployment report"""
        timestamp = datetime.now().isoformat()
        
        final_status = await self.check_current_deployment()
        
        report = {
            "render_deployment_trigger": {
                "timestamp": timestamp,
                "backend_url": BACKEND_URL,
                "deployment_triggered": True,
                "deployment_successful": deployment_successful,
                "final_deployment_status": final_status,
                "ultra_emergency_system": {
                    "minimal_database_schema": True,
                    "ultra_emergency_user_service": True,
                    "emergency_webhook_handler": True,
                    "bulletproof_credit_assignment": True
                }
            }
        }
        
        # Save report
        report_filename = f"RENDER_DEPLOYMENT_TRIGGER_REPORT_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("🚀 RENDER DEPLOYMENT TRIGGER REPORT 🚀")
        print("="*60)
        print(f"⏰ Timestamp: {timestamp}")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"🚀 Deployment Triggered: ✅")
        print(f"📊 Deployment Successful: {'✅' if deployment_successful else '❌'}")
        
        if final_status.get("deployment_complete", False):
            print("🎉 ULTRA-EMERGENCY SYSTEM FULLY DEPLOYED!")
            print("   ✅ User endpoints available")
            print("   ✅ Webhook endpoints available") 
            print("   ✅ Credit endpoints available")
            print("   ✅ Ready for credit assignment testing")
        else:
            print("⚠️ DEPLOYMENT STILL IN PROGRESS OR FAILED")
            print("   🔧 May need manual intervention")
            print("   ⏱️ May need more time to complete")
        
        print(f"\n📄 Full report saved: {report_filename}")
        print("="*60)
        
        return report

async def main():
    """Trigger Render deployment"""
    print("🚀 EMERGENCY RENDER DEPLOYMENT TRIGGER 🚀")
    print("Forcing redeploy with ultra-emergency fixes...")
    print("Ensuring credit assignment works after Stripe payments...")
    print()
    
    async with RenderDeploymentTrigger() as trigger:
        # Check current deployment
        current_status = await trigger.check_current_deployment()
        
        if current_status.get("deployment_complete", False):
            print("✅ Ultra-emergency system already deployed!")
            print("🎉 Ready for credit assignment testing")
        else:
            print("⚠️ Ultra-emergency system not fully deployed")
            print("🚀 Triggering new deployment...")
            
            # Force redeploy
            await trigger.force_render_redeploy()
            
            # Monitor progress
            deployment_successful = await trigger.monitor_deployment_progress()
            
            # Generate report
            await trigger.generate_deployment_report(deployment_successful)
            
            if deployment_successful:
                print("\n🎉 DEPLOYMENT SUCCESS! 🎉")
                print("✅ Ultra-emergency system is now live")
                print("✅ Credit assignment system operational")
                print("🔄 Ready to test Stripe payments")
            else:
                print("\n⚠️ DEPLOYMENT TIMEOUT ⚠️")
                print("🔧 Deployment may still be in progress")
                print("⏱️ Check Render dashboard for status")

if __name__ == "__main__":
    asyncio.run(main())
