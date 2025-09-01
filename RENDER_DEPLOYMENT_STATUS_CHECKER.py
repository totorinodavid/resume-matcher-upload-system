#!/usr/bin/env python3
"""
EMERGENCY RENDER DEPLOYMENT STATUS CHECK
Überprüft den Status des Render-Deployments für das Resume-Matcher Backend
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

# Render deployment URLs to check
DEPLOYMENT_URLS = [
    "https://resume-matcher-backend-j06k.onrender.com",
    "https://resume-matcher-backend-j06k.onrender.com/",
    "https://resume-matcher-backend-j06k.onrender.com/docs",
    "https://resume-matcher-backend-j06k.onrender.com/api/v1/health"
]

class RenderDeploymentChecker:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_url(self, url):
        """Check a specific URL"""
        try:
            logger.info(f"🌐 Checking: {url}")
            start_time = time.time()
            
            async with self.session.get(url) as response:
                response_time = time.time() - start_time
                status = response.status
                
                if status == 200:
                    try:
                        data = await response.json()
                        logger.info(f"✅ {url} - Status: {status} - Time: {response_time:.2f}s - JSON: {data}")
                        return {"url": url, "status": status, "response_time": response_time, "type": "json", "data": data}
                    except:
                        text = await response.text()
                        logger.info(f"✅ {url} - Status: {status} - Time: {response_time:.2f}s - HTML/Text response")
                        return {"url": url, "status": status, "response_time": response_time, "type": "html", "length": len(text)}
                else:
                    logger.error(f"❌ {url} - Status: {status} - Time: {response_time:.2f}s")
                    return {"url": url, "status": status, "response_time": response_time, "type": "error"}
                    
        except asyncio.TimeoutError:
            logger.error(f"⏰ {url} - TIMEOUT")
            return {"url": url, "status": "TIMEOUT", "error": "Request timeout"}
        except Exception as e:
            logger.error(f"❌ {url} - ERROR: {e}")
            return {"url": url, "status": "ERROR", "error": str(e)}

    async def check_deployment_status(self):
        """Check all deployment URLs"""
        results = []
        
        for url in DEPLOYMENT_URLS:
            result = await self.check_url(url)
            results.append(result)
            await asyncio.sleep(2)  # Wait between requests
            
        return results

    async def generate_status_report(self, results):
        """Generate deployment status report"""
        timestamp = datetime.now().isoformat()
        
        # Analyze results
        working_urls = [r for r in results if isinstance(r.get("status"), int) and r["status"] == 200]
        error_urls = [r for r in results if r.get("status") != 200]
        
        deployment_status = "ONLINE" if len(working_urls) > 0 else "OFFLINE"
        health_check_working = any(r.get("url", "").endswith("/health") and r.get("status") == 200 for r in results)
        
        report = {
            "render_deployment_check": {
                "timestamp": timestamp,
                "deployment_status": deployment_status,
                "health_check_working": health_check_working,
                "working_urls": len(working_urls),
                "total_urls": len(results),
                "response_times": [r.get("response_time", 0) for r in working_urls],
                "avg_response_time": sum(r.get("response_time", 0) for r in working_urls) / len(working_urls) if working_urls else 0,
                "detailed_results": results
            }
        }
        
        # Save report
        report_filename = f"RENDER_DEPLOYMENT_STATUS_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("🚀 RENDER DEPLOYMENT STATUS REPORT 🚀")
        print("="*60)
        print(f"⏰ Timestamp: {timestamp}")
        print(f"🌐 Deployment Status: {'🟢 ONLINE' if deployment_status == 'ONLINE' else '🔴 OFFLINE'}")
        print(f"❤️ Health Check: {'✅ Working' if health_check_working else '❌ Failed'}")
        print(f"📊 URLs: {len(working_urls)}/{len(results)} working")
        print(f"⚡ Avg Response Time: {sum(r.get('response_time', 0) for r in working_urls) / len(working_urls) if working_urls else 0:.2f}s")
        
        print("\n📋 URL Status Details:")
        for result in results:
            url = result.get("url", "Unknown")
            status = result.get("status", "Unknown")
            response_time = result.get("response_time", 0)
            
            if status == 200:
                print(f"   ✅ {url} - {status} ({response_time:.2f}s)")
            elif status == "TIMEOUT":
                print(f"   ⏰ {url} - TIMEOUT")
            else:
                print(f"   ❌ {url} - {status}")
        
        print(f"\n📄 Full report saved: {report_filename}")
        print("="*60)
        
        return report

async def main():
    """Check Render deployment status"""
    print("🚀 CHECKING RENDER DEPLOYMENT STATUS 🚀")
    print("Verifying Resume-Matcher backend availability...")
    print()
    
    async with RenderDeploymentChecker() as checker:
        # Check deployment status
        results = await checker.check_deployment_status()
        
        # Generate report
        report = await checker.generate_status_report(results)
        
        # Provide next steps
        if report["render_deployment_check"]["deployment_status"] == "ONLINE":
            print("\n🎉 RENDER DEPLOYMENT IS ONLINE! 🎉")
            if report["render_deployment_check"]["health_check_working"]:
                print("✅ Health check endpoint is working")
                print("🔄 Can proceed with emergency deployment test")
            else:
                print("⚠️ Health check endpoint not responding")
                print("🔧 Backend may be starting up or health endpoint missing")
        else:
            print("\n⚠️ RENDER DEPLOYMENT IS OFFLINE ⚠️")
            print("🔧 Possible issues:")
            print("   - Backend is starting up (Render free tier sleeps)")
            print("   - Deployment failed")
            print("   - Wrong URL")
            print("   - Network issues")
            print("\n💡 Next steps:")
            print("   1. Check Render dashboard for deployment status")
            print("   2. Wait a few minutes for cold start")
            print("   3. Check deployment logs")

if __name__ == "__main__":
    asyncio.run(main())
