#!/usr/bin/env python3
"""
🔍 FINALE STRIPE CREDITS LIVE-DIAGNOSE
=====================================

Testet das automatisch gepatched System in der Live-Umgebung.
Validiert alle Verbesserungen und gibt finale Handlungsempfehlungen.

ZIEL: Identifiziere die EXAKTE Ursache warum Credits nicht hinzugefügt werden.
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class FinalStripeCreditsLiveDiagnose:
    def __init__(self):
        self.frontend_url = "https://gojob.ing"
        self.backend_url = "https://resume-matcher-backend-j06k.onrender.com"
        
        self.critical_issues = []
        self.recommendations = []
        
    def log(self, level: str, message: str, detail: str = ""):
        """Enhanced logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", 
            "ERROR": "❌", "CRITICAL": "🚨", "FIX": "🔧", "TEST": "🧪"
        }
        print(f"[{timestamp}] {icons.get(level, '📋')} {message}")
        if detail:
            print(f"         {detail}")
    
    def test_backend_health_and_webhook(self) -> Dict[str, any]:
        """Kritischer Test: Backend Health & Webhook Verfügbarkeit"""
        self.log("TEST", "KRITISCHER TEST: Backend & Webhook Status")
        
        results = {}
        
        # 1. Backend Health Check
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=15)
            if response.status_code == 200:
                self.log("SUCCESS", "Backend ist LIVE und erreichbar")
                results["backend_health"] = True
            else:
                self.log("CRITICAL", f"Backend Health Check fehlgeschlagen: {response.status_code}")
                results["backend_health"] = False
                self.critical_issues.append("Backend nicht verfügbar")
        except Exception as e:
            self.log("CRITICAL", "Backend komplett unerreichbar", str(e))
            results["backend_health"] = False
            self.critical_issues.append(f"Backend Error: {str(e)}")
        
        # 2. Webhook Endpoint Verfügbarkeit
        try:
            # Test mit minimaler Stripe-kompatible Payload
            minimal_webhook = {
                "id": "evt_test_webhook",
                "object": "event",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_123",
                        "object": "checkout.session",
                        "customer": None,
                        "metadata": {
                            "user_id": "test_user_live",
                            "credits": "100",
                            "price_id": "price_test"
                        }
                    }
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/webhooks/stripe",
                json=minimal_webhook,
                headers={
                    "Stripe-Signature": "t=1693906800,v1=test_signature_for_diagnosis",
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            
            self.log("INFO", f"Webhook Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    webhook_result = response.json()
                    self.log("SUCCESS", "Webhook endpoint erreichbar")
                    self.log("INFO", f"Webhook Response: {webhook_result}")
                    
                    if webhook_result.get("skipped") == "no_user_mapping":
                        self.log("CRITICAL", "🚨 HAUPTPROBLEM IDENTIFIZIERT: User-ID Mapping fehlt!")
                        self.critical_issues.append("Webhook kann User-ID nicht aus Metadata extrahieren")
                        self.recommendations.append("User-ID Extraktion in Webhook reparieren")
                    elif webhook_result.get("ok"):
                        self.log("SUCCESS", "Webhook verarbeitet Events korrekt")
                    
                    results["webhook_available"] = True
                    results["webhook_response"] = webhook_result
                    
                except Exception as e:
                    self.log("WARNING", "Webhook antwortet nicht als JSON", str(e))
                    results["webhook_available"] = True
                    results["webhook_response"] = "non_json"
                    
            elif response.status_code == 400:
                self.log("INFO", "Webhook lehnt ab (Signatur-Problem, aber erreichbar)")
                results["webhook_available"] = True
                results["webhook_response"] = "signature_error"
                
            elif response.status_code == 404:
                self.log("CRITICAL", "Webhook Endpoint existiert nicht!")
                self.critical_issues.append("Webhook Route /webhooks/stripe nicht implementiert")
                results["webhook_available"] = False
                
            else:
                self.log("WARNING", f"Webhook unerwartete Response: {response.status_code}")
                results["webhook_available"] = "unknown"
                
        except Exception as e:
            self.log("CRITICAL", "Webhook komplett unerreichbar", str(e))
            results["webhook_available"] = False
            self.critical_issues.append(f"Webhook Error: {str(e)}")
            
        return results
    
    def test_frontend_auth_and_checkout(self) -> Dict[str, any]:
        """Test Frontend Authentication & Checkout"""
        self.log("TEST", "Frontend Authentication & Checkout Test")
        
        results = {}
        
        # 1. Session Status
        try:
            response = requests.get(f"{self.frontend_url}/api/auth/session", timeout=10)
            if response.status_code == 200:
                try:
                    session = response.json()
                    if session and session.get("user"):
                        user_id = session["user"].get("id")
                        self.log("SUCCESS", f"User eingeloggt: {user_id}")
                        results["user_logged_in"] = True
                        results["user_id"] = user_id
                    else:
                        self.log("WARNING", "Kein User in Session - MELDEN SIE SICH AN!")
                        results["user_logged_in"] = False
                        self.recommendations.append("🔴 KRITISCH: Melden Sie sich in gojob.ing an und wiederholen Sie die Diagnose")
                except:
                    self.log("WARNING", "Session-Endpoint antwortet aber kein JSON")
                    results["user_logged_in"] = "unknown"
            else:
                self.log("WARNING", f"Session-Endpoint Status: {response.status_code}")
                results["user_logged_in"] = "error"
        except Exception as e:
            self.log("ERROR", "Session-Test fehlgeschlagen", str(e))
            results["user_logged_in"] = "error"
        
        # 2. Checkout Authentication
        try:
            response = requests.post(
                f"{self.frontend_url}/api/stripe/checkout",
                json={"price_id": "price_test"},
                timeout=10
            )
            
            if response.status_code == 401:
                self.log("SUCCESS", "Checkout erfordert Authentication (korrekt)")
                results["checkout_auth"] = True
            elif response.status_code == 400:
                self.log("INFO", "Checkout lehnt Price-ID ab (aber Auth OK)")
                results["checkout_auth"] = True
            else:
                self.log("WARNING", f"Checkout Authentication ungewöhnlich: {response.status_code}")
                results["checkout_auth"] = False
                
        except Exception as e:
            self.log("ERROR", "Checkout-Test fehlgeschlagen", str(e))
            results["checkout_auth"] = "error"
            
        return results
    
    def simulate_complete_purchase_flow(self) -> Dict[str, any]:
        """Simuliert kompletten Kaufvorgang"""
        self.log("TEST", "🎯 SIMULATION: Kompletter Kaufvorgang")
        
        results = {}
        
        # Simuliere einen authentifizierten Checkout
        mock_checkout_session = {
            "id": "cs_test_live_simulation",
            "object": "checkout.session", 
            "customer": None,
            "customer_details": {
                "email": "test@example.com"
            },
            "metadata": {
                "user_id": "live_test_user_123",
                "credits": "100", 
                "price_id": "price_test_live",
                "purchase_timestamp": datetime.now().isoformat(),
                "frontend_version": "1.0"
            },
            "amount_total": 999,
            "currency": "eur",
            "payment_status": "paid"
        }
        
        # Simuliere Webhook-Event
        webhook_event = {
            "id": "evt_live_test",
            "object": "event",
            "type": "checkout.session.completed",
            "data": {
                "object": mock_checkout_session
            },
            "created": int(datetime.now().timestamp())
        }
        
        self.log("INFO", "Sende simulierten Webhook...")
        self.log("INFO", f"User-ID in Simulation: {mock_checkout_session['metadata']['user_id']}")
        
        try:
            response = requests.post(
                f"{self.backend_url}/webhooks/stripe",
                json=webhook_event,
                headers={
                    "Stripe-Signature": "t=1693906800,v1=simulation_signature",
                    "Content-Type": "application/json"
                },
                timeout=15
            )
            
            self.log("INFO", f"Webhook Simulation Response: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.log("SUCCESS", f"Webhook Response: {result}")
                    
                    if result.get("skipped") == "no_user_mapping":
                        self.log("CRITICAL", "🚨 PROBLEM BESTÄTIGT: User-ID Mapping funktioniert nicht!")
                        self.critical_issues.append("Webhook extrahiert User-ID nicht aus Metadata")
                        self.recommendations.append("Überprüfen Sie _resolve_user_id Funktion in webhooks.py")
                        
                    elif result.get("skipped") == "no_mapped_prices":
                        self.log("CRITICAL", "🚨 PROBLEM: Price-ID Mapping fehlt!")
                        self.critical_issues.append("Price-IDs nicht in Environment Variables")
                        self.recommendations.append("Setzen Sie STRIPE_PRICE_* Environment Variables")
                        
                    elif result.get("ok"):
                        self.log("SUCCESS", "🎉 Simulation erfolgreich - Webhook funktioniert!")
                        results["simulation_success"] = True
                        
                    else:
                        self.log("WARNING", f"Unbekannte Webhook Response: {result}")
                        
                    results["webhook_result"] = result
                    
                except Exception as e:
                    self.log("ERROR", "Webhook Response Parse Error", str(e))
                    results["webhook_result"] = "parse_error"
                    
            elif response.status_code == 400:
                self.log("INFO", "Webhook Signatur-Validierung (normal für Test)")
                results["webhook_result"] = "signature_validation"
                
            else:
                self.log("ERROR", f"Webhook Simulation fehlgeschlagen: {response.status_code}")
                results["webhook_result"] = f"error_{response.status_code}"
                
        except Exception as e:
            self.log("CRITICAL", "Webhook Simulation komplett fehlgeschlagen", str(e))
            results["webhook_result"] = "connection_error"
            self.critical_issues.append(f"Webhook nicht erreichbar: {str(e)}")
            
        return results
    
    def provide_final_solution(self):
        """Finale Lösung basierend auf allen Tests"""
        self.log("FIX", "🎯 FINALE LÖSUNG & HANDLUNGSEMPFEHLUNGEN")
        
        print("\n" + "="*80)
        print("🎯 STRIPE CREDITS PROBLEM - FINALE DIAGNOSE")
        print("="*80)
        
        if not self.critical_issues:
            print("✅ SYSTEM FUNKTIONIERT GRUNDSÄTZLICH!")
            print("   Das Problem liegt wahrscheinlich bei der User-Session.")
            print()
            print("🔧 SOFORT-LÖSUNG:")
            print("   1. Melden Sie sich bei https://gojob.ing an")
            print("   2. Führen Sie einen Test-Kauf durch")
            print("   3. Überprüfen Sie die Browser-Konsole auf Fehler")
            print("   4. Überprüfen Sie die Webhook-Logs in Render")
            return
        
        print("🚨 KRITISCHE PROBLEME IDENTIFIZIERT:")
        for i, issue in enumerate(self.critical_issues, 1):
            print(f"   {i}. ❌ {issue}")
        
        print()
        print("💡 PRIORITÄRE LÖSUNGSSCHRITTE:")
        for i, rec in enumerate(self.recommendations, 1):
            print(f"   {i}. 🔧 {rec}")
        
        print()
        print("🎯 SOFORTIGE HANDLUNGEN:")
        
        if any("Backend" in issue for issue in self.critical_issues):
            print("   🔥 HÖCHSTE PRIORITÄT: Backend/Render Server Problem")
            print("      → Überprüfen Sie Render Dashboard")
            print("      → Checken Sie Server-Logs")
            print("      → Starten Sie Service neu wenn nötig")
        
        elif any("Webhook" in issue for issue in self.critical_issues):
            print("   🔥 HÖCHSTE PRIORITÄT: Webhook Implementation Problem") 
            print("      → Überprüfen Sie apps/backend/app/api/router/webhooks.py")
            print("      → Stellen Sie sicher dass _resolve_user_id funktioniert")
            print("      → Testen Sie lokale Webhook-Verarbeitung")
        
        elif any("User-ID" in issue for issue in self.critical_issues):
            print("   🔥 MITTLERE PRIORITÄT: User-ID Mapping Problem")
            print("      → Überprüfen Sie Checkout Session Metadata")
            print("      → Validieren Sie NextAuth User-Session")
            print("      → Debuggen Sie User-ID Extraktion")
        
        elif any("Price-ID" in issue for issue in self.critical_issues):
            print("   🔥 NIEDRIGE PRIORITÄT: Environment Configuration")
            print("      → Setzen Sie STRIPE_PRICE_* Variables in Render")
            print("      → Verwenden Sie STRIPE_ENVIRONMENT_TEMPLATE.env als Vorlage")
        
        print()
        print("📋 DEBUGGING-BEFEHLE:")
        print("   • python stripe_credits_autodiagnose.py   # Wiederhole Diagnose")
        print("   • python test_stripe_credits_fixed.py     # Teste Fixes")
        print("   • Check Render Logs: https://dashboard.render.com")
        print("   • Check Stripe Dashboard: https://dashboard.stripe.com")
    
    def run_final_diagnosis(self):
        """Hauptfunktion: Finale Live-Diagnose"""
        print("🔍 FINALE STRIPE CREDITS LIVE-DIAGNOSE")
        print("="*80)
        print(f"🌐 Frontend: {self.frontend_url}")
        print(f"🖥️  Backend: {self.backend_url}")
        print(f"⏰ Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Sequentielle Tests
        backend_results = self.test_backend_health_and_webhook()
        print()
        
        frontend_results = self.test_frontend_auth_and_checkout()
        print()
        
        simulation_results = self.simulate_complete_purchase_flow()
        print()
        
        # Finale Lösung
        self.provide_final_solution()

if __name__ == "__main__":
    final_diagnose = FinalStripeCreditsLiveDiagnose()
    final_diagnose.run_final_diagnosis()
