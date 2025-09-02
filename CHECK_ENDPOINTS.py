#!/usr/bin/env python3
"""
Check what endpoints are available on the backend
"""

import asyncio
import aiohttp

async def check_available_endpoints():
    print("🔍 CHECKING AVAILABLE ENDPOINTS")
    print("================================")
    
    base_url = "https://resume-matcher-backend-service.onrender.com"
    
    # Test various endpoint patterns
    endpoints_to_test = [
        "/",
        "/health",
        "/healthz", 
        "/api",
        "/api/v1",
        "/api/v1/health",
        "/api/webhooks",
        "/api/webhooks/stripe",
        "/docs",
        "/openapi.json"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints_to_test:
            url = f"{base_url}{endpoint}"
            try:
                async with session.get(url, timeout=10) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', 'unknown')
                    
                    if status < 400:
                        print(f"✅ {endpoint} -> {status} ({content_type})")
                    else:
                        print(f"❌ {endpoint} -> {status}")
                        
            except asyncio.TimeoutError:
                print(f"⏰ {endpoint} -> TIMEOUT")
            except Exception as e:
                print(f"💥 {endpoint} -> ERROR: {e}")

async def test_simple_webhook():
    print("\n🧪 TESTING WEBHOOK ENDPOINT")
    print("============================")
    
    base_url = "https://resume-matcher-backend-service.onrender.com"
    webhook_url = f"{base_url}/api/webhooks/stripe"
    
    # Simple test payload
    test_data = {"test": "webhook"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(webhook_url, json=test_data, timeout=10) as response:
                status = response.status
                text = await response.text()
                
                print(f"📡 Webhook Status: {status}")
                print(f"📄 Webhook Response: {text}")
                
        except Exception as e:
            print(f"❌ Webhook test failed: {e}")

async def main():
    await check_available_endpoints()
    await test_simple_webhook()

if __name__ == "__main__":
    asyncio.run(main())
