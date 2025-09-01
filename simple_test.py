#!/usr/bin/env python3
"""
Simple test using requests (standard library alternative)
"""

import json
try:
    from urllib.request import urlopen, Request, HTTPError
    from urllib.error import URLError
    
    def test_endpoint():
        print("🔍 TESTING ADMIN ENDPOINT")
        print("=" * 30)
        
        url = "https://resume-matcher-backend-j06k.onrender.com/admin/credits/e747de39-1b54-4cd0-96eb-e68f155931e2"
        
        try:
            print("Testing admin endpoint...")
            
            request = Request(url)
            with urlopen(request, timeout=30) as response:
                status_code = response.getcode()
                content = response.read().decode('utf-8')
                
                print(f"Status: {status_code}")
                print(f"Response: {content}")
                
                if status_code == 200:
                    data = json.loads(content)
                    print(f"✅ SUCCESS! Your balance: {data['total_credits']} credits")
                    return True
                else:
                    print("❌ Still has issues")
                    return False
                    
        except HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.read().decode('utf-8')}")
            return False
        except URLError as e:
            print(f"❌ URL Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    if __name__ == "__main__":
        success = test_endpoint()
        if success:
            print("\n🎉 READY FOR CREDIT TRANSFER!")
        else:
            print("\n⏳ Deployment still updating...")
            
except ImportError:
    print("Could not import urllib. Using alternative approach...")
    print("Please wait for deployment to complete and try again.")
