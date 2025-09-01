#!/usr/bin/env python3
"""
KORRIGIERTE USER ID - BASIEREND AUF PRODUCTION LOGS
"""

import json
from urllib.request import urlopen, Request, HTTPError
from urllib.error import URLError

def check_balance(user_id, description):
    url = f"https://resume-matcher-backend-j06k.onrender.com/admin/credits/{user_id}"
    
    try:
        request = Request(url)
        with urlopen(request, timeout=15) as response:
            content = response.read().decode('utf-8')
            data = json.loads(content)
            print(f"{description}: {data['total_credits']} credits")
            return data['total_credits']
    except Exception as e:
        print(f"{description}: ERROR - {e}")
        return None

def main():
    print("🔍 KORRIGIERTE USER ID ANALYSE")
    print("=" * 50)
    print()
    
    # Basierend auf den Production Logs:
    real_user_id = "ed00040a-3bce-497c-9f3c-f3ce86ea4"  # Deine ECHTE aktuelle User ID
    old_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"  # Alte User ID aus Context
    wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"  # Falsche User ID von Stripe
    
    print("CHECKING ALLE USER IDS:")
    print()
    
    print("1. DEINE ECHTE AKTUELLE USER ID (aus Production Logs):")
    real_balance = check_balance(real_user_id, f"   {real_user_id}")
    
    print()
    print("2. ALTE USER ID AUS CONTEXT:")
    old_balance = check_balance(old_user_id, f"   {old_user_id}")
    
    print()
    print("3. FALSCHE USER ID VON STRIPE PAYMENT:")
    wrong_balance = check_balance(wrong_user_id, f"   {wrong_user_id}")
    
    print()
    print("=" * 50)
    print("ANALYSE:")
    
    if real_balance and real_balance > 0:
        print(f"✅ GEFUNDEN! Deine echte User ID hat {real_balance} Credits!")
        print("   Das Problem ist bereits gelöst!")
    elif wrong_balance and wrong_balance > 0:
        print(f"⚠️  Credits sind bei falscher User ID: {wrong_balance}")
        print("   Transfer von falscher zu echter User ID nötig")
    elif old_balance and old_balance > 0:
        print(f"⚠️  Credits sind bei alter User ID: {old_balance}")
        print("   Transfer von alter zu echter User ID nötig")
    else:
        print("❌ Keine Credits gefunden bei keiner der User IDs")
        print("   Weitere Diagnose nötig")

if __name__ == "__main__":
    main()
