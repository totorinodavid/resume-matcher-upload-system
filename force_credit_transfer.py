#!/usr/bin/env python3
"""
FORCE CREDIT TRANSFER - Umgeht alle Balance-Checks
"""

import json
import time
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

def force_transfer_credits(from_user, to_user, amount):
    url = "https://resume-matcher-backend-j06k.onrender.com/admin/force-transfer-credits"
    
    transfer_data = {
        "from_user_id": from_user,
        "to_user_id": to_user,
        "amount": amount,
        "reason": "emergency_fix_wrong_stripe_assignment"
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

def wait_for_deployment():
    print("⏳ Warte auf Deployment der neuen Force-Transfer Methode...")
    
    for i in range(6):  # 3 Minuten warten
        print(f"   Versuch {i+1}/6...")
        time.sleep(30)
        
        # Test ob neuer Endpoint verfügbar ist
        try:
            url = "https://resume-matcher-backend-j06k.onrender.com/admin/force-transfer-credits"
            test_data = {"from_user_id": "test", "to_user_id": "test", "amount": 1, "reason": "test"}
            request = Request(url, 
                             data=json.dumps(test_data).encode('utf-8'),
                             headers={'Content-Type': 'application/json'})
            
            with urlopen(request, timeout=15) as response:
                # Wenn wir hier sind, ist der Endpoint verfügbar (auch wenn er einen Fehler zurückgibt)
                print("✅ Neuer Endpoint ist verfügbar!")
                return True
        except HTTPError as e:
            if e.code == 500:  # Interne Fehler sind OK, bedeutet Endpoint existiert
                print("✅ Neuer Endpoint ist verfügbar!")
                return True
        except:
            pass
    
    print("⚠️ Deployment dauert länger als erwartet, versuche trotzdem...")
    return False

def main():
    print("🚀 FORCE CREDIT TRANSFER")
    print("=" * 40)
    print()
    
    your_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
    wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"
    amount = 50
    
    print("BALANCES VOR TRANSFER:")
    your_balance = check_balance(your_user_id, "Deine Balance")
    wrong_balance = check_balance(wrong_user_id, "Falsche User ID Balance")
    
    print()
    
    # Warte auf Deployment
    wait_for_deployment()
    
    print()
    print(f"🚀 FÜHRE FORCE TRANSFER DURCH: {amount} Credits")
    print(f"   VON: {wrong_user_id}")
    print(f"   ZU:  {your_user_id}")
    
    success, result = force_transfer_credits(wrong_user_id, your_user_id, amount)
    
    if success:
        print("✅ FORCE TRANSFER ERFOLGREICH!")
        print(f"   Methode: {result.get('method', 'unknown')}")
        print(f"   Transferiert: {result['transferred']} credits")
        print(f"   Deine neue Balance: {result['to_user_final_balance']} credits")
        print()
        print("🎉 PROBLEM ENDLICH GELÖST!")
    else:
        print(f"❌ FORCE TRANSFER FEHLGESCHLAGEN: {result}")
    
    print()
    print("FINALE BALANCES:")
    check_balance(your_user_id, "Deine finale Balance")
    check_balance(wrong_user_id, "Falsche User ID finale Balance")

if __name__ == "__main__":
    main()
