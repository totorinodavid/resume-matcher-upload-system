#!/usr/bin/env python3
"""
🚀 AUTOMATISCHE DEPLOYMENT-ÜBERWACHUNG
=====================================

Überwacht das Render Deployment und testet die Stripe Credits Fixes
sobald das System wieder online ist.

FUNKTIONEN:
- Kontinuierliche Backend-Überwachung
- Automatischer Test nach Deployment
- Live-Statusberichte
- Sofortige Problemerkennung
"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

class DeploymentMonitor:
    def __init__(self):
        self.backend_url = "https://resume-matcher-backend-j06k.onrender.com"
        self.frontend_url = "https://gojob.ing"
        
        self.deployment_start = datetime.now()
        self.max_wait_minutes = 15  # Maximale Wartezeit
        
    def log(self, level: str, message: str, detail: str = ""):
        """Logging mit Zeitstempel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", 
            "ERROR": "❌", "DEPLOY": "🚀", "TEST": "🧪"
        }
        print(f"[{timestamp}] {icons.get(level, '📋')} {message}")
        if detail:
            print(f"         {detail}")
    
    def check_backend_health(self) -> Dict[str, any]:
        """Überprüft Backend-Verfügbarkeit"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                return {"status": "online", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "error", "code": response.status_code}
        except requests.exceptions.Timeout:
            return {"status": "timeout"}
        except requests.exceptions.ConnectionError:
            return {"status": "connection_error"}
        except Exception as e:
            return {"status": "unknown_error", "error": str(e)}
    
    def test_webhook_endpoint(self) -> Dict[str, any]:
        """Testet Webhook-Endpoint Verfügbarkeit"""
        test_webhook = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_deployment_test",
                    "customer": None,
                    "metadata": {
                        "user_id": "deployment_test_user",
                        "credits": "100",
                        "price_id": "price_test"
                    }
                }
            }
        }
        
        try:
            response = requests.post(
                f"{self.backend_url}/webhooks/stripe",
                json=test_webhook,
                headers={"Stripe-Signature": "t=1693906800,v1=deployment_test"},
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return {"status": "ok", "response": result}
                except:
                    return {"status": "ok", "response": "non_json"}
            elif response.status_code == 400:
                return {"status": "signature_validation", "response": "expected"}
            else:
                return {"status": "error", "code": response.status_code}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def run_comprehensive_test(self) -> Dict[str, any]:
        """Führt umfassenden Test nach Deployment durch"""
        self.log("TEST", "🎯 UMFASSENDER POST-DEPLOYMENT TEST")
        
        results = {}
        
        # 1. Backend Health
        health = self.check_backend_health()
        results["backend_health"] = health
        
        if health["status"] == "online":
            self.log("SUCCESS", f"Backend online (Response: {health['response_time']:.2f}s)")
        else:
            self.log("ERROR", f"Backend Status: {health['status']}")
            return results
        
        # 2. Webhook Test
        webhook = self.test_webhook_endpoint()
        results["webhook"] = webhook
        
        if webhook["status"] == "ok":
            self.log("SUCCESS", "Webhook-Endpoint funktioniert")
            if isinstance(webhook.get("response"), dict):
                webhook_response = webhook["response"]
                if webhook_response.get("skipped") == "no_user_mapping":
                    self.log("WARNING", "⚠️ User-ID Mapping Problem weiterhin vorhanden")
                elif webhook_response.get("ok"):
                    self.log("SUCCESS", "🎉 Webhook verarbeitet Events korrekt!")
        elif webhook["status"] == "signature_validation":
            self.log("SUCCESS", "Webhook-Endpoint erreichbar (Signatur-Validierung funktioniert)")
        else:
            self.log("ERROR", f"Webhook Problem: {webhook}")
        
        # 3. Frontend Test
        try:
            response = requests.get(f"{self.frontend_url}/api/auth/session", timeout=10)
            if response.status_code == 200:
                self.log("SUCCESS", "Frontend Session-Endpoint erreichbar")
                results["frontend"] = {"status": "ok"}
            else:
                self.log("WARNING", f"Frontend Session Status: {response.status_code}")
                results["frontend"] = {"status": "warning", "code": response.status_code}
        except Exception as e:
            self.log("ERROR", f"Frontend nicht erreichbar: {str(e)}")
            results["frontend"] = {"status": "error", "error": str(e)}
        
        return results
    
    def monitor_deployment(self):
        """Hauptfunktion: Überwacht Deployment"""
        print("🚀 AUTOMATISCHE DEPLOYMENT-ÜBERWACHUNG GESTARTET")
        print("="*70)
        print(f"🎯 Backend: {self.backend_url}")
        print(f"🌐 Frontend: {self.frontend_url}")
        print(f"⏰ Start: {self.deployment_start.strftime('%H:%M:%S')}")
        print(f"⏳ Max Wartezeit: {self.max_wait_minutes} Minuten")
        print()
        
        check_interval = 30  # Alle 30 Sekunden prüfen
        checks_count = 0
        
        while True:
            elapsed = datetime.now() - self.deployment_start
            
            # Timeout check
            if elapsed > timedelta(minutes=self.max_wait_minutes):
                self.log("ERROR", f"🕐 TIMEOUT nach {self.max_wait_minutes} Minuten")
                self.log("ERROR", "Deployment dauert ungewöhnlich lange")
                self.log("INFO", "Überprüfen Sie Render Dashboard manuell")
                break
            
            checks_count += 1
            elapsed_str = f"{int(elapsed.total_seconds() // 60)}:{int(elapsed.total_seconds() % 60):02d}"
            
            self.log("INFO", f"🔍 Check #{checks_count} (Elapsed: {elapsed_str})")
            
            # Backend Health Check
            health = self.check_backend_health()
            
            if health["status"] == "online":
                self.log("SUCCESS", "🎉 BACKEND IST ONLINE!")
                self.log("SUCCESS", f"Response Time: {health['response_time']:.2f}s")
                
                # Kurz warten damit Deployment vollständig abgeschlossen ist
                self.log("INFO", "Warte 30s für vollständiges Deployment...")
                time.sleep(30)
                
                # Umfassenden Test durchführen
                test_results = self.run_comprehensive_test()
                
                # Zusammenfassung
                print("\n" + "="*70)
                print("🎯 DEPLOYMENT-TEST ZUSAMMENFASSUNG")
                print("="*70)
                
                if test_results.get("backend_health", {}).get("status") == "online":
                    print("✅ Backend: ONLINE")
                else:
                    print("❌ Backend: PROBLEM")
                
                webhook_status = test_results.get("webhook", {}).get("status")
                if webhook_status in ["ok", "signature_validation"]:
                    print("✅ Webhook: FUNKTIONIERT")
                else:
                    print("❌ Webhook: PROBLEM")
                
                frontend_status = test_results.get("frontend", {}).get("status")
                if frontend_status == "ok":
                    print("✅ Frontend: ONLINE")
                else:
                    print("⚠️ Frontend: PRÜFEN ERFORDERLICH")
                
                print()
                print("🚀 NÄCHSTE SCHRITTE:")
                print("   1. Melden Sie sich bei https://gojob.ing an")
                print("   2. Führen Sie einen Test-Kauf durch")
                print("   3. Überprüfen Sie ob Credits hinzugefügt werden")
                print("   4. Bei Problemen: python final_stripe_credits_live_diagnose.py")
                
                break
            
            elif health["status"] == "timeout":
                self.log("WARNING", "🕐 Backend Timeout (Deployment läuft...)")
            elif health["status"] == "connection_error":
                self.log("INFO", "🔌 Backend nicht erreichbar (Deployment läuft...)")
            elif health["status"] == "error":
                self.log("WARNING", f"🚨 Backend Error: {health.get('code', 'unknown')}")
            else:
                self.log("WARNING", f"🤔 Backend Status: {health}")
            
            # Warten bis zum nächsten Check
            self.log("INFO", f"⏳ Nächster Check in {check_interval}s...")
            time.sleep(check_interval)

if __name__ == "__main__":
    monitor = DeploymentMonitor()
    monitor.monitor_deployment()
