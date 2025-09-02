#!/usr/bin/env python3
"""
GOOGLE OAUTH ENVIRONMENT CHECKER
Validates Google OAuth configuration for production deployment
"""

import os
import requests
import json

def check_google_oauth_config():
    """Check Google OAuth configuration"""
    
    print("🔍 GOOGLE OAUTH CONFIGURATION CHECK")
    print("=" * 50)
    
    # Check if environment variables are set
    required_vars = [
        'AUTH_SECRET',
        'AUTH_GOOGLE_ID', 
        'AUTH_GOOGLE_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("\n📋 Required Google OAuth Setup:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create OAuth 2.0 Client IDs")
        print("3. Add authorized origins:")
        print("   - https://gojob.ing")
        print("   - https://www.gojob.ing")
        print("4. Add authorized redirect URIs:")
        print("   - https://gojob.ing/api/auth/callback/google")
        print("   - https://www.gojob.ing/api/auth/callback/google")
        print("5. Set environment variables in Vercel")
        return False
    
    print("✅ All required environment variables are set")
    
    # Test Google OAuth discovery
    try:
        discovery_url = "https://accounts.google.com/.well-known/openid_configuration"
        response = requests.get(discovery_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Google OAuth discovery endpoint accessible")
        else:
            print(f"⚠️  Google OAuth discovery returned {response.status_code}")
    
    except Exception as e:
        print(f"⚠️  Could not reach Google OAuth discovery: {e}")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Deploy the auth fixes to Vercel")
    print("2. Check Google Console for valid redirect URIs") 
    print("3. Verify environment variables in Vercel dashboard")
    
    return True

if __name__ == "__main__":
    check_google_oauth_config()
