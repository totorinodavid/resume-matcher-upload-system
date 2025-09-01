#!/usr/bin/env python3
"""
DIREKTE DATENBANK CREDIT SUCHE
Sucht nach allen Credit-Einträgen für beide User IDs
"""

import json
from urllib.request import urlopen, Request, HTTPError
from urllib.error import URLError

def check_all_credits():
    print("🔍 SUCHE NACH ALLEN CREDIT EINTRÄGEN")
    print("=" * 50)
    print()
    
    your_user_id = "e747de39-1b54-4cd0-96eb-e68f155931e2"
    wrong_user_id = "7675e93c-341b-412d-a41c-cfe1dc519172"
    
    # Mögliche alternative User IDs oder Varianten
    possible_ids = [
        your_user_id,
        wrong_user_id,
        # Möglicherweise andere Varianten
        "e747de39-1b54-4cd0-96eb-e68f155931e2",  # deine korrekte
        "7675e93c-341b-412d-a41c-cfe1dc519172",  # falsche aus Logs
    ]
    
    print("Überprüfe alle möglichen User IDs:")
    for i, user_id in enumerate(possible_ids):
        print(f"\n{i+1}. User ID: {user_id}")
        try:
            url = f"https://resume-matcher-backend-j06k.onrender.com/admin/credits/{user_id}"
            request = Request(url)
            with urlopen(request, timeout=15) as response:
                content = response.read().decode('utf-8')
                data = json.loads(content)
                balance = data['total_credits']
                print(f"   ✅ Balance: {balance} credits")
                
                if balance > 0:
                    print(f"   🎯 GEFUNDEN! Diese User ID hat {balance} credits!")
                    
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
    
    print("\n" + "="*50)
    print("WEITERE DIAGNOSTIK BENÖTIGT")
    print("Die Credits könnten sein:")
    print("1. In einer anderen User ID")
    print("2. In einer anderen Tabelle")
    print("3. Noch nicht richtig committet")
    print("4. Durch einen anderen Prozess verarbeitet")
    
    print("\nBASIEREND AUF DEINEN PRODUCTION LOGS:")
    print("Event ID: evt_1S2YsxEPwuWwkzKTxZFOrvZG")
    print("Session: cs_test_a1SJt9iWMLHX1QsTNaufdzf42Cqe50BBgUWS1brZPF2nW0wSwOLCX1DBXs")
    print("Metadata user_id: 7675e93c-341b-412d-a41c-cfe1dc519172")
    print("SUCCESS: 50 credits added to user 7675e93c-341b-412d-a41c-cfe1dc519172")
    print("\nDiese User ID sollte definitiv 50 Credits haben!")

if __name__ == "__main__":
    check_all_credits()
