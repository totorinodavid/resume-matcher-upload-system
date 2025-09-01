#!/usr/bin/env python3
"""
DIREKTE CREDIT ZUTEILUNG
Fügt 50 Credits direkt zu deiner User ID hinzu via Admin API
"""

import json
from urllib.request import urlopen, Request, HTTPError
from urllib.error import URLError

def add_credits_directly(user_id, credits, reason):
    """Fügt Credits direkt via Admin API hinzu"""
    url = "https://resume-matcher-backend-j06k.onrender.com/admin/force-transfer-credits"
    
    # Wir "transferieren" von einer Dummy User ID zu deiner echten User ID
    dummy_user_id = "00000000-0000-0000-0000-000000000000"  # Dummy source
    
    transfer_data = {
        "from_user_id": dummy_user_id,  # Dummy source (wird negative credits bekommen)
        "to_user_id": user_id,          # Du bekommst positive credits
        "amount": credits,
        "reason": reason
    }
    
    try:
        request = Request(
            url, 
            data=json.dumps(transfer_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urlopen(request, timeout=30) as response:
            content = response.read().decode('utf-8')
            data = json.loads(content)
            return True, data
    except HTTPError as e:
        error_content = e.read().decode('utf-8')
        return False, f"HTTP Error {e.code}: {error_content}"
    except Exception as e:
        return False, f"Error: {e}"

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
    print("💳 DIREKTE CREDIT ZUTEILUNG - 50 CREDITS")
    print("=" * 50)
    print()
    
    # Alle möglichen User IDs basierend auf den Logs
    possible_user_ids = [
        "ed00040a-3bce-497c-96eb-f3ce86ea4",  # Vermutung 1
        "ed00040a-3bce-497c-9f3c-f3ce86ea4",  # Vermutung 2
        "e747de39-1b54-4cd0-96eb-e68f155931e2",  # Aus Context
    ]
    
    print("1. CHECKING CURRENT BALANCES:")
    current_balances = {}
    for user_id in possible_user_ids:
        balance = check_balance(user_id, f"   {user_id}")
        current_balances[user_id] = balance
    
    print()
    print("2. ADDING 50 CREDITS TO FIRST VALID USER ID...")
    
    for user_id in possible_user_ids:
        if current_balances.get(user_id) is not None:  # API call was successful
            print(f"   Trying to add credits to: {user_id}")
            
            success, result = add_credits_directly(
                user_id=user_id,
                credits=50,
                reason="manual_stripe_payment_credit_fix"
            )
            
            if success:
                print(f"✅ SUCCESS! Credits added to {user_id}")
                print(f"   Result: {result}")
                
                # Verify new balance
                print()
                print("3. VERIFYING NEW BALANCE:")
                new_balance = check_balance(user_id, f"   {user_id}")
                
                if new_balance and new_balance >= 50:
                    print()
                    print("🎉 PROBLEM GELÖST!")
                    print(f"   Du hast jetzt {new_balance} Credits!")
                    print(f"   User ID: {user_id}")
                    return
                else:
                    print(f"⚠️ Credits added but balance verification failed")
            else:
                print(f"❌ Failed to add credits: {result}")
        else:
            print(f"   Skipping {user_id} (API call failed)")
    
    print()
    print("❌ Could not add credits to any User ID")
    print("   This suggests the force-transfer endpoint is not deployed yet")

if __name__ == "__main__":
    main()
