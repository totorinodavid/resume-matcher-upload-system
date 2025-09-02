"""
🚀 LIVE CREDITS SYSTEM TEST
Test the production credits system in real-time
"""
import requests
import time

BASE_URL = "https://resume-matcher-backend-j06k.onrender.com"

def test_credits_endpoints():
    """Test all credits-related endpoints"""
    print("🚀 TESTING PRODUCTION CREDITS SYSTEM")
    print("=" * 50)
    
    # Test 1: Basic health check
    print("\n1️⃣ Testing health endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"   /health: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   /health: ERROR - {e}")
    
    # Test 2: API endpoints
    print("\n2️⃣ Testing API structure...")
    endpoints_to_test = [
        "/docs",
        "/api/v1/health", 
        "/webhooks/stripe"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   {endpoint}: ERROR - {str(e)[:50]}")
    
    # Test 3: Credits API endpoints (should exist now)
    print("\n3️⃣ Testing Credits API...")
    credits_endpoints = [
        "/api/v1/credits/balance",
        "/api/v1/payments/create-checkout",
    ]
    
    for endpoint in credits_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 422:  # Validation error is expected for GET requests
                print(f"      ✅ Endpoint exists (422 = validation error for missing data)")
            elif response.status_code == 404:
                print(f"      ❌ Endpoint not found")
            else:
                print(f"      ✅ Endpoint responding")
        except Exception as e:
            print(f"   {endpoint}: ERROR - {str(e)[:50]}")
    
    print("\n4️⃣ Checking if credits system is deployed...")
    # Check if the credits system is actually working
    try:
        # This should return the OpenAPI docs which will show all endpoints
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            
            # Look for credits-related endpoints
            credits_paths = [path for path in paths.keys() if 'credit' in path.lower() or 'payment' in path.lower()]
            
            if credits_paths:
                print(f"   ✅ Credits endpoints found: {len(credits_paths)}")
                for path in credits_paths[:5]:  # Show first 5
                    print(f"      - {path}")
            else:
                print(f"   ❌ No credits endpoints found in API")
                print(f"   📋 Available paths: {len(paths)} total")
                
        else:
            print(f"   ⚠️  OpenAPI not accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ OpenAPI check failed: {e}")

def monitor_deployment_progress():
    """Monitor deployment until credits system is live"""
    print("\n⏱️  MONITORING DEPLOYMENT PROGRESS...")
    print("Waiting for credits system to be fully deployed...")
    
    for attempt in range(10):  # 5 minutes max
        print(f"\n[Attempt {attempt + 1}/10]")
        test_credits_endpoints()
        
        if attempt < 9:
            print("\n⏳ Waiting 30s for next check...")
            time.sleep(30)
        else:
            print("\n🎯 Monitoring complete!")

if __name__ == "__main__":
    monitor_deployment_progress()
