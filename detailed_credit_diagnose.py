#!/usr/bin/env python3
"""
DETAILLIERTE CREDIT DIAGNOSE
Überprüfe beide User IDs und führe einen manuellen Transfer durch
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

def transfer_credits(from_user, to_user, amount):
    url = "https://resume-matcher-backend-j06k.onrender.com/admin/transfer-credits"
    
    transfer_data = {
        "from_user_id": from_user,
        "to_user_id": to_user,
        "amount": amount,
        "reason": "manual_fix_wrong_user_assignment"
    }
    
    try:
        request = Request(url, 
                         data=json.dumps(transfer_data).encode('utf-8'),
                         headers={'Content-Type': 'application/json'})
        
        with urlopen(request, timeout=30) as response:
            content = response.read().decode('utf-8')
            data = json.loads(content)
            return True, data
    except HTTPError as e:
        error_content = e.read().decode('utf-8')
        return False, f"HTTP Error {e.code}: {error_content}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("🔍 DETAILLIERTE CREDIT DIAGNOSE")
    print("=" * 50)
    print()
    
    your_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
    wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"
    
    print("AKTUELLE BALANCES:")
    your_balance = check_balance(your_user_id, "Deine korrekte User ID")
    wrong_balance = check_balance(wrong_user_id, "Falsche User ID (mit Credits)")
    
    print()
    
    if wrong_balance and wrong_balance > 0:
        print(f"✅ Gefunden: {wrong_balance} Credits bei falscher User ID")
        print("🚀 STARTE TRANSFER...")
        
        success, result = transfer_credits(wrong_user_id, your_user_id, wrong_balance)
        
        if success:
            print("✅ TRANSFER ERFOLGREICH!")
            print(f"   Transferiert: {result['transferred']} credits")
            print(f"   Deine neue Balance: {result['to_user_final_balance']} credits")
        else:
            print(f"❌ TRANSFER FEHLGESCHLAGEN: {result}")
    else:
        print("❌ Keine Credits bei falscher User ID gefunden")
        print("   Möglicherweise wurden sie bereits transferiert oder sind nicht vorhanden")
    
    print()
    print("FINALE BALANCES:")
    check_balance(your_user_id, "Deine finale Balance")
    check_balance(wrong_user_id, "Falsche User ID finale Balance")

if __name__ == "__main__":
    main()
