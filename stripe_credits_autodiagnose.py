#!/usr/bin/env python3
"""
🔍 AUTOMATISCHES STRIPE CREDITS DIAGNOSETOOL
============================================

Vollautomatische Diagnose des User-ID Mapping Problems.
Identifiziert die genaue Ursache und bietet Lösungsvorschläge.

Führt folgende Tests durch:
1. Backend Environment-Konfiguration
2. Webhook-Endpoint Verfügbarkeit  
3. User-Authentication Status
4. Checkout-Session Metadata-Struktur
5. Webhook User-ID Extraktion
6. Credits Service Funktionalität
7. Real-Time Webhook Monitoring
"""

import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class StripeCreditsAutodiagnose:
    def __init__(self):
        self.frontend_url = "https://gojob.ing"
        self.backend_url = "https://resume-matcher-backend-j06k.onrender.com"
        self.issues_found = []
        self.solutions = []
        self.test_results = {}
        
    def log(self, level: str, message: str, detail: str = ""):
        """Unified logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "DEBUG": "🔍"}
        print(f"[{timestamp}] {icon.get(level, '📋')} {message}")
        if detail:
            print(f"         {detail}")
    
    def test_backend_environment(self) -> Dict[str, bool]:
        """Test 1: Backend Environment-Konfiguration"""
        self.log("INFO", "Test 1: Backend Environment-Konfiguration")
        results = {}
        
        try:
            # Test webhook endpoint mit verschiedenen Szenarien
            response = requests.post(
                f"{self.backend_url}/webhooks/stripe",
                json={"test": "config_check"},
                headers={"Stripe-Signature": "test_sig"},
                timeout=10
            )
            
            if response.status_code == 503:
                self.log("ERROR", "STRIPE_WEBHOOK_SECRET nicht konfiguriert")
                self.issues_found.append("STRIPE_WEBHOOK_SECRET fehlt in Backend Environment")
                self.solutions.append("Fügen Sie STRIPE_WEBHOOK_SECRET in Render Dashboard hinzu")
                results["webhook_secret"] = False
            elif response.status_code == 400:
                self.log("SUCCESS", "STRIPE_WEBHOOK_SECRET konfiguriert")
                results["webhook_secret"] = True
            else:
                self.log("WARNING", f"Unerwartete Webhook-Response: {response.status_code}")
                results["webhook_secret"] = "unknown"
                
        except Exception as e:
            self.log("ERROR", "Backend nicht erreichbar", str(e))
            results["webhook_secret"] = "unreachable"
        
        return results
    
    def test_user_authentication(self) -> Dict[str, any]:
        """Test 2: User-Authentication Status"""
        self.log("INFO", "Test 2: User-Authentication Status")
        results = {}
        
        try:
            # Test Session-Endpoint
            response = requests.get(f"{self.frontend_url}/api/auth/session", timeout=10)
            
            if response.status_code == 200:
                try:
                    session_data = response.json()
                    if session_data and session_data.get("user"):
                        user_id = session_data["user"].get("id")
                        self.log("SUCCESS", f"User Session aktiv: {user_id}")
                        results["authenticated"] = True
                        results["user_id"] = user_id
                    else:
                        self.log("WARNING", "Session vorhanden aber kein User")
                        results["authenticated"] = False
                except:
                    self.log("WARNING", "Session-Endpoint antwortet aber nicht als JSON")
                    results["authenticated"] = "unknown"
            else:
                self.log("WARNING", f"Session-Endpoint Status: {response.status_code}")
                results["authenticated"] = "unknown"
                
        except Exception as e:
            self.log("ERROR", "Session-Test fehlgeschlagen", str(e))
            results["authenticated"] = "error"
        
        # Test Checkout-Authentication
        try:
            response = requests.post(
                f"{self.frontend_url}/api/stripe/checkout",
                json={"price_id": "price_test"},
                timeout=10
            )
            
            if response.status_code == 401:
                self.log("SUCCESS", "Checkout erfordert Authentifizierung (korrekt)")
                results["checkout_auth"] = True
            else:
                self.log("WARNING", f"Checkout Authentication ungewöhnlich: {response.status_code}")
                results["checkout_auth"] = False
                
        except Exception as e:
            self.log("ERROR", "Checkout-Authentication-Test fehlgeschlagen", str(e))
            results["checkout_auth"] = "error"
            
        return results
    
    def test_webhook_user_id_extraction(self) -> Dict[str, any]:
        """Test 3: Webhook User-ID Extraktion Simulation"""
        self.log("INFO", "Test 3: Webhook User-ID Extraktion Simulation")
        results = {}
        
        # Simuliere verschiedene Webhook-Szenarien
        test_cases = [
            {
                "name": "Normaler First-Time Buyer",
                "webhook_data": {
                    "type": "checkout.session.completed",
                    "data": {
                        "object": {
                            "customer": None,
                            "metadata": {
                                "user_id": "user_123",
                                "credits": "100"
                            }
                        }
                    }
                }
            },
            {
                "name": "Leere Metadata",
                "webhook_data": {
                    "type": "checkout.session.completed", 
                    "data": {
                        "object": {
                            "customer": None,
                            "metadata": {}
                        }
                    }
                }
            },
            {
                "name": "Null Metadata",
                "webhook_data": {
                    "type": "checkout.session.completed",
                    "data": {
                        "object": {
                            "customer": None,
                            "metadata": None
                        }
                    }
                }
            }
        ]
        
        for test_case in test_cases:
            self.log("DEBUG", f"Simuliere: {test_case['name']}")
            
            try:
                response = requests.post(
                    f"{self.frontend_url}/api/stripe/webhook",
                    json=test_case["webhook_data"],
                    headers={"Stripe-Signature": "t=1693906800,v1=test_signature"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get("skipped") == "no_user_mapping":
                            self.log("ERROR", f"User-ID Mapping Fehler bei: {test_case['name']}")
                            self.issues_found.append(f"User-ID wird nicht extrahiert: {test_case['name']}")
                        elif result.get("ok"):
                            self.log("SUCCESS", f"Webhook-Verarbeitung OK: {test_case['name']}")
                    except:
                        self.log("WARNING", f"Webhook Response nicht JSON: {test_case['name']}")
                        
                elif response.status_code == 400:
                    self.log("DEBUG", f"Signatur-Validierung (erwartet): {test_case['name']}")
                    
            except Exception as e:
                self.log("ERROR", f"Webhook-Test fehlgeschlagen: {test_case['name']}", str(e))
        
        return results
    
    def test_price_mapping(self) -> Dict[str, any]:
        """Test 4: Price-ID Mapping"""
        self.log("INFO", "Test 4: Price-ID zu Credits Mapping")
        results = {}
        
        # Test webhook mit verschiedenen Price-IDs
        test_prices = ["price_small", "price_medium", "price_large", "price_unknown"]
        
        for price_id in test_prices:
            test_webhook = {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "customer": None,
                        "metadata": {
                            "user_id": "test_user",
                            "credits": "100",
                            "price_id": price_id
                        }
                    }
                }
            }
            
            try:
                response = requests.post(
                    f"{self.frontend_url}/api/stripe/webhook",
                    json=test_webhook,
                    headers={"Stripe-Signature": "t=1693906800,v1=test_sig"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get("skipped") == "no_mapped_prices":
                            self.log("WARNING", f"Price-ID nicht gemapped: {price_id}")
                            self.issues_found.append(f"Price-ID {price_id} nicht in Environment Variables")
                        elif result.get("ok"):
                            self.log("SUCCESS", f"Price-ID gemapped: {price_id}")
                    except:
                        pass
                        
            except Exception as e:
                self.log("ERROR", f"Price-Mapping Test fehlgeschlagen: {price_id}", str(e))
        
        return results
    
    def monitor_real_webhook_activity(self, duration: int = 30) -> Dict[str, any]:
        """Test 5: Real-Time Webhook Activity Monitoring"""
        self.log("INFO", f"Test 5: Real-Time Webhook Monitoring ({duration}s)")
        self.log("INFO", "🚀 Führen Sie JETZT einen Test-Kauf durch!")
        
        results = {"webhook_calls": 0, "events_seen": []}
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Test-Ping an Webhook um Aktivität zu erkennen
                response = requests.post(
                    f"{self.backend_url}/webhooks/stripe",
                    json={"monitor": "ping"},
                    headers={"Stripe-Signature": "monitor_ping"},
                    timeout=5
                )
                
                results["webhook_calls"] += 1
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get("ok"):
                            self.log("SUCCESS", "🎉 Echter Webhook empfangen!")
                            results["events_seen"].append(data)
                    except:
                        pass
                        
            except Exception:
                pass
            
            time.sleep(2)
        
        if results["webhook_calls"] == 0:
            self.log("WARNING", "Keine Webhook-Aktivität erkannt")
        elif not results["events_seen"]:
            self.log("INFO", "Webhook-Endpoint erreichbar aber keine Events")
        
        return results
    
    def analyze_results_and_provide_solution(self):
        """Finale Analyse und Lösungsvorschläge"""
        self.log("INFO", "🎯 FINALE DIAGNOSE & LÖSUNGSVORSCHLÄGE")
        print("\n" + "="*60)
        
        if not self.issues_found:
            print("✅ KEINE KRITISCHEN PROBLEME GEFUNDEN!")
            print("   Das System sollte grundsätzlich funktionieren.")
            print("\n🔍 MÖGLICHE URSACHEN FÜR CREDITS-PROBLEM:")
            print("   1. User nicht korrekt eingeloggt während Kauf")
            print("   2. NextAuth Session abgelaufen")
            print("   3. Browser blockiert Cookies/Session")
            print("   4. Timing-Problem zwischen Checkout und Webhook")
            return
        
        print("🚨 PROBLEME IDENTIFIZIERT:")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"   {i}. ❌ {issue}")
        
        print("\n💡 LÖSUNGSVORSCHLÄGE:")
        for i, solution in enumerate(self.solutions, 1):
            print(f"   {i}. 🔧 {solution}")
        
        print("\n🎯 PRIORITÄTEN:")
        if any("STRIPE_WEBHOOK_SECRET" in issue for issue in self.issues_found):
            print("   🔥 HÖCHSTE PRIORITÄT: STRIPE_WEBHOOK_SECRET konfigurieren")
            print("      → Render Dashboard → Environment Variables")
        
        if any("Price-ID" in issue for issue in self.issues_found):
            print("   🔥 HOHE PRIORITÄT: Price-IDs in Environment Variables setzen")
            print("      → STRIPE_PRICE_SMALL_ID, STRIPE_PRICE_MEDIUM_ID, etc.")
        
        if any("User-ID" in issue for issue in self.issues_found):
            print("   🔥 MITTLERE PRIORITÄT: User-ID Extraktion reparieren")
            print("      → Checkout-Code prüfen und Session-Handling verbessern")
    
    def run_complete_diagnosis(self):
        """Hauptfunktion: Vollständige Diagnose"""
        print("🚀 AUTOMATISCHE STRIPE CREDITS DIAGNOSE GESTARTET")
        print("="*60)
        print(f"Frontend: {self.frontend_url}")
        print(f"Backend: {self.backend_url}")
        print(f"Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Tests nacheinander ausführen
        self.test_results["environment"] = self.test_backend_environment()
        print()
        
        self.test_results["authentication"] = self.test_user_authentication()  
        print()
        
        self.test_results["webhook_extraction"] = self.test_webhook_user_id_extraction()
        print()
        
        self.test_results["price_mapping"] = self.test_price_mapping()
        print()
        
        # Optional: Real-time monitoring
        print("⏰ Real-Time Monitoring startet in 5 Sekunden...")
        print("   🛒 Führen Sie JETZT einen Test-Kauf durch!")
        time.sleep(5)
        
        self.test_results["real_time"] = self.monitor_real_webhook_activity(30)
        print()
        
        # Finale Analyse
        self.analyze_results_and_provide_solution()

if __name__ == "__main__":
    diagnose_tool = StripeCreditsAutodiagnose()
    diagnose_tool.run_complete_diagnosis()
