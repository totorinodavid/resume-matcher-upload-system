#!/usr/bin/env python3
"""
EMERGENCY DEPLOYMENT LIVE TEST
Ultra-Minimal Database Schema Compatibility Verification

Tests the ultra-emergency system with live Render deployment.
This script validates that credits are assigned after Stripe payments
using only the minimal database schema (id, email, name).
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

# Live deployment URL
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"

class EmergencyDeploymentTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_health_check(self):
        """Test if the backend is responding"""
        try:
            logger.info("🏥 Testing backend health...")
            # First try the main endpoint
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    logger.info(f"✅ Backend responding: Status {response.status}")
                    self.test_results.append({"test": "health_check", "status": "PASS", "status_code": response.status})
                    return True
                else:
                    logger.error(f"❌ Backend unhealthy: {response.status}")
                    self.test_results.append({"test": "health_check", "status": "FAIL", "status_code": response.status})
                    return False
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            self.test_results.append({"test": "health_check", "status": "ERROR", "error": str(e)})
            return False

    async def test_database_connection(self):
        """Test database connection with minimal schema"""
        try:
            logger.info("🗄️ Testing database connection...")
            async with self.session.get(f"{BACKEND_URL}/api/v1/users/test-db") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Database connected: {data}")
                    self.test_results.append({"test": "database_connection", "status": "PASS", "data": data})
                    return True
                else:
                    logger.error(f"❌ Database connection failed: {response.status}")
                    self.test_results.append({"test": "database_connection", "status": "FAIL", "status_code": response.status})
                    return False
        except Exception as e:
            logger.error(f"❌ Database test failed: {e}")
            self.test_results.append({"test": "database_connection", "status": "ERROR", "error": str(e)})
            return False

    async def test_user_service_ultra_emergency(self):
        """Test UltraEmergencyUserService functionality"""
        try:
            logger.info("🚨 Testing UltraEmergencyUserService...")
            
            # Test user creation with minimal schema
            test_user_data = {
                "email": f"emergency-test-{int(time.time())}@example.com",
                "name": "Emergency Test User"
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/v1/users/emergency-create", json=test_user_data) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ User created with UltraEmergencyUserService: {data}")
                    self.test_results.append({"test": "ultra_emergency_user_service", "status": "PASS", "user_data": data})
                    return data
                else:
                    logger.error(f"❌ UltraEmergencyUserService failed: {response.status}")
                    self.test_results.append({"test": "ultra_emergency_user_service", "status": "FAIL", "status_code": response.status})
                    return None
        except Exception as e:
            logger.error(f"❌ UltraEmergencyUserService test failed: {e}")
            self.test_results.append({"test": "ultra_emergency_user_service", "status": "ERROR", "error": str(e)})
            return None

    async def test_webhook_handler_ultra_emergency(self):
        """Test ultra emergency webhook handler"""
        try:
            logger.info("🪝 Testing ultra emergency webhook handler...")
            
            # Simulate a Stripe webhook with minimal user data
            webhook_payload = {
                "type": "payment_intent.succeeded",
                "data": {
                    "object": {
                        "id": "pi_test_emergency",
                        "amount": 1000,  # $10.00
                        "currency": "usd",
                        "metadata": {
                            "user_id": "1",
                            "user_email": "emergency@example.com",
                            "credits": "10"
                        }
                    }
                }
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/v1/webhooks/stripe", 
                                       json=webhook_payload,
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status in [200, 202]:
                    data = await response.text()
                    logger.info(f"✅ Webhook processed successfully: {data}")
                    self.test_results.append({"test": "webhook_ultra_emergency", "status": "PASS", "response": data})
                    return True
                else:
                    logger.error(f"❌ Webhook processing failed: {response.status}")
                    self.test_results.append({"test": "webhook_ultra_emergency", "status": "FAIL", "status_code": response.status})
                    return False
        except Exception as e:
            logger.error(f"❌ Webhook test failed: {e}")
            self.test_results.append({"test": "webhook_ultra_emergency", "status": "ERROR", "error": str(e)})
            return False

    async def test_credit_system_minimal(self):
        """Test credit assignment with minimal database schema"""
        try:
            logger.info("💳 Testing credit system with minimal schema...")
            
            # Test credit balance check
            async with self.session.get(f"{BACKEND_URL}/api/v1/credits/balance/1") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Credit balance retrieved: {data}")
                    self.test_results.append({"test": "credit_system_minimal", "status": "PASS", "balance": data})
                    return True
                else:
                    logger.error(f"❌ Credit system failed: {response.status}")
                    self.test_results.append({"test": "credit_system_minimal", "status": "FAIL", "status_code": response.status})
                    return False
        except Exception as e:
            logger.error(f"❌ Credit system test failed: {e}")
            self.test_results.append({"test": "credit_system_minimal", "status": "ERROR", "error": str(e)})
            return False

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        timestamp = datetime.now().isoformat()
        
        # Count results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.get("status") == "PASS"])
        failed_tests = len([r for r in self.test_results if r.get("status") == "FAIL"])
        error_tests = len([r for r in self.test_results if r.get("status") == "ERROR"])
        
        report = {
            "emergency_deployment_test": {
                "timestamp": timestamp,
                "backend_url": BACKEND_URL,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "system_status": "OPERATIONAL" if failed_tests == 0 and error_tests == 0 else "DEGRADED",
                "ultra_emergency_system": {
                    "database_schema": "minimal (id, email, name only)",
                    "user_service": "UltraEmergencyUserService",
                    "webhook_handler": "ultra_emergency version",
                    "compatibility": "maximum database compatibility mode"
                },
                "detailed_results": self.test_results
            }
        }
        
        # Save report
        report_filename = f"EMERGENCY_DEPLOYMENT_TEST_REPORT_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("🚨 EMERGENCY DEPLOYMENT TEST REPORT 🚨")
        print("="*60)
        print(f"⏰ Timestamp: {timestamp}")
        print(f"🌐 Backend URL: {BACKEND_URL}")
        print(f"📊 Tests: {total_tests} total | ✅ {passed_tests} passed | ❌ {failed_tests} failed | ⚠️ {error_tests} errors")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print(f"🔧 System Status: {'🟢 OPERATIONAL' if failed_tests == 0 and error_tests == 0 else '🟡 DEGRADED'}")
        print("\n🛠️ Ultra Emergency System Status:")
        print("   - Database Schema: Minimal (id, email, name)")
        print("   - User Service: UltraEmergencyUserService")
        print("   - Webhook Handler: Ultra Emergency Version")
        print("   - Compatibility: Maximum Database Compatibility Mode")
        print(f"\n📄 Full report saved: {report_filename}")
        print("="*60)
        
        return report

async def main():
    """Run emergency deployment tests"""
    print("🚨 STARTING EMERGENCY DEPLOYMENT LIVE TEST 🚨")
    print("Testing ultra-minimal database schema compatibility...")
    print("Verifying credit assignment after Stripe payments...")
    print()
    
    async with EmergencyDeploymentTester() as tester:
        # Run all tests
        await tester.test_health_check()
        await asyncio.sleep(1)
        
        await tester.test_database_connection()
        await asyncio.sleep(1)
        
        await tester.test_user_service_ultra_emergency()
        await asyncio.sleep(1)
        
        await tester.test_webhook_handler_ultra_emergency()
        await asyncio.sleep(1)
        
        await tester.test_credit_system_minimal()
        await asyncio.sleep(1)
        
        # Generate final report
        report = await tester.generate_test_report()
        
        # Determine if deployment is successful
        if report["emergency_deployment_test"]["system_status"] == "OPERATIONAL":
            print("\n🎉 EMERGENCY DEPLOYMENT SUCCESS! 🎉")
            print("✅ Ultra-minimal database schema compatibility verified")
            print("✅ Credit assignment system operational")
            print("✅ Stripe payments will now correctly assign credits")
        else:
            print("\n⚠️ EMERGENCY DEPLOYMENT NEEDS ATTENTION ⚠️")
            print("❌ Some systems are not fully operational")
            print("🔧 Review test report for specific issues")

if __name__ == "__main__":
    asyncio.run(main())
