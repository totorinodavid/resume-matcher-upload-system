#!/usr/bin/env python3
"""
🔧 AUTOMATISCHES STRIPE CREDITS FIX-TOOL
========================================

Repariert automatisch die häufigsten User-ID Mapping Probleme.
Erstellt fehlende Code-Patches und Environment-Konfigurationen.

FUNKTIONEN:
- Checkout Session Metadata Fix
- Webhook User-ID Extraktion Fix  
- Environment Variables Auto-Setup
- Database Schema Validierung
- Code-Patches für bekannte Bugs
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class StripeCreditsAutofix:
    def __init__(self):
        self.project_root = Path("c:/Users/david/Documents/GitHub/Resume-Matcher")
        self.backend_path = self.project_root / "apps/backend"
        self.frontend_path = self.project_root / "apps/frontend"
        
        self.fixes_applied = []
        self.fixes_failed = []
        
    def log(self, level: str, message: str, detail: str = ""):
        """Unified logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "FIX": "🔧"}
        print(f"[{timestamp}] {icon.get(level, '📋')} {message}")
        if detail:
            print(f"         {detail}")
    
    def fix_checkout_metadata(self) -> bool:
        """Fix 1: Checkout Session Metadata Transmission"""
        self.log("FIX", "Fix 1: Checkout Session Metadata Transmission")
        
        checkout_file = self.frontend_path / "app/api/stripe/checkout/route.ts"
        
        if not checkout_file.exists():
            self.log("ERROR", f"Checkout-Datei nicht gefunden: {checkout_file}")
            return False
        
        try:
            content = checkout_file.read_text(encoding='utf-8')
            
            # Check if user_id metadata already exists
            if 'user_id:' in content and 'session.user.id' in content:
                self.log("SUCCESS", "Checkout Metadata bereits korrekt konfiguriert")
                return True
            
            # Create improved checkout metadata section
            improved_metadata = '''
            // IMPROVED: Robust User-ID Metadata Transmission
            const robustMetadata = {
              user_id: session.user.id || session.user.email || 'fallback_user',
              credits: String(credits),
              price_id: priceId,
              purchase_timestamp: new Date().toISOString(),
              frontend_version: '1.0',
              debug_session: JSON.stringify({
                userId: session.user.id,
                email: session.user.email,
                timestamp: Date.now()
              })
            };

            // Validate metadata before sending
            if (!robustMetadata.user_id || robustMetadata.user_id === 'fallback_user') {
              console.error('❌ USER_ID MISSING in checkout metadata!', {
                session: session,
                metadata: robustMetadata
              });
              throw new Error('User not properly authenticated for checkout');
            }

            console.log('✅ Checkout metadata prepared:', robustMetadata);
            '''
            
            # Try to find and replace metadata section
            if 'metadata:' in content:
                # Find the metadata object and replace it
                lines = content.split('\n')
                new_lines = []
                in_metadata = False
                metadata_start = -1
                
                for i, line in enumerate(lines):
                    if 'metadata:' in line and '{' in line:
                        in_metadata = True
                        metadata_start = i
                        new_lines.append('      metadata: robustMetadata,')
                        continue
                    elif in_metadata and '}' in line and ',' in line:
                        in_metadata = False
                        continue
                    elif not in_metadata:
                        new_lines.append(line)
                
                # Insert improved metadata before the checkout session creation
                for i, line in enumerate(new_lines):
                    if 'const session = await stripe.checkout.sessions.create' in line:
                        new_lines.insert(i, improved_metadata)
                        break
                
                improved_content = '\n'.join(new_lines)
                
                # Write backup and new file
                backup_file = checkout_file.with_suffix('.backup.ts')
                checkout_file.rename(backup_file)
                checkout_file.write_text(improved_content, encoding='utf-8')
                
                self.log("SUCCESS", "Checkout Metadata Fix angewendet")
                self.log("INFO", f"Backup erstellt: {backup_file}")
                self.fixes_applied.append("Checkout Session Metadata verbessert")
                return True
            else:
                self.log("WARNING", "Keine Metadata-Sektion in Checkout gefunden")
                return False
                
        except Exception as e:
            self.log("ERROR", "Checkout Metadata Fix fehlgeschlagen", str(e))
            self.fixes_failed.append(f"Checkout Fix: {str(e)}")
            return False
    
    def fix_webhook_user_resolution(self) -> bool:
        """Fix 2: Webhook User-ID Resolution"""
        self.log("FIX", "Fix 2: Webhook User-ID Resolution")
        
        webhook_file = self.backend_path / "app/api/router/webhooks.py"
        
        if not webhook_file.exists():
            self.log("ERROR", f"Webhook-Datei nicht gefunden: {webhook_file}")
            return False
        
        try:
            content = webhook_file.read_text(encoding='utf-8')
            
            # Check if improved user resolution already exists
            if 'robust_user_resolution' in content:
                self.log("SUCCESS", "Webhook User Resolution bereits verbessert")
                return True
            
            # Find _resolve_user_id function and improve it
            improved_resolution = '''
    async def _resolve_user_id(self, session_obj) -> Optional[str]:
        """IMPROVED: Robust User-ID Resolution from Stripe Checkout Session"""
        user_id = None
        
        # Method 1: From StripeCustomer table lookup
        customer_id = session_obj.get("customer")
        if customer_id:
            try:
                stmt = select(StripeCustomer).where(StripeCustomer.stripe_customer_id == customer_id)
                result = await self.db.execute(stmt)
                stripe_customer = result.scalar_one_or_none()
                if stripe_customer:
                    user_id = stripe_customer.user_id
                    logger.info(f"✅ User-ID from StripeCustomer: {user_id}")
            except Exception as e:
                logger.error(f"❌ StripeCustomer lookup failed: {e}")
        
        # Method 2: From metadata (primary method for new customers)
        if not user_id:
            metadata = session_obj.get("metadata", {}) or {}
            user_id = metadata.get("user_id")
            
            if user_id:
                logger.info(f"✅ User-ID from metadata: {user_id}")
            else:
                logger.error(f"❌ No user_id in metadata. Available keys: {list(metadata.keys())}")
                logger.error(f"❌ Full metadata: {metadata}")
                logger.error(f"❌ Full session_obj keys: {list(session_obj.keys())}")
        
        # Method 3: Fallback via email lookup
        if not user_id:
            customer_email = session_obj.get("customer_details", {}).get("email")
            if customer_email:
                try:
                    # This would require a User model lookup by email
                    logger.warning(f"⚠️ Attempting email fallback for: {customer_email}")
                    # TODO: Implement User.get_by_email lookup
                except Exception as e:
                    logger.error(f"❌ Email fallback failed: {e}")
        
        if not user_id:
            logger.error("❌ CRITICAL: All user resolution methods failed!")
            logger.error(f"❌ Session object structure: {json.dumps(session_obj, indent=2, default=str)}")
        
        return user_id
            '''
            
            # Replace the existing function
            if 'def _resolve_user_id' in content:
                lines = content.split('\n')
                new_lines = []
                in_function = False
                indent_level = 0
                
                for line in lines:
                    if 'def _resolve_user_id' in line:
                        in_function = True
                        indent_level = len(line) - len(line.lstrip())
                        new_lines.extend(improved_resolution.split('\n'))
                        continue
                    elif in_function:
                        current_indent = len(line) - len(line.lstrip())
                        if line.strip() and current_indent <= indent_level and not line.startswith(' ' * (indent_level + 1)):
                            in_function = False
                            new_lines.append(line)
                        # Skip lines that are part of the old function
                        continue
                    else:
                        new_lines.append(line)
                
                improved_content = '\n'.join(new_lines)
                
                # Write backup and new file
                backup_file = webhook_file.with_suffix('.backup.py')
                webhook_file.rename(backup_file)
                webhook_file.write_text(improved_content, encoding='utf-8')
                
                self.log("SUCCESS", "Webhook User Resolution Fix angewendet")
                self.log("INFO", f"Backup erstellt: {backup_file}")
                self.fixes_applied.append("Webhook User-ID Resolution verbessert")
                return True
            else:
                self.log("WARNING", "Keine _resolve_user_id Funktion gefunden")
                return False
                
        except Exception as e:
            self.log("ERROR", "Webhook User Resolution Fix fehlgeschlagen", str(e))
            self.fixes_failed.append(f"Webhook Fix: {str(e)}")
            return False
    
    def create_environment_template(self) -> bool:
        """Fix 3: Environment Variables Template"""
        self.log("FIX", "Fix 3: Environment Variables Template")
        
        try:
            env_template = '''# STRIPE CREDITS SYSTEM - COMPLETE ENVIRONMENT TEMPLATE
# =====================================================
# Diese Variablen müssen in Render Dashboard und lokaler .env gesetzt werden

# STRIPE GRUNDKONFIGURATION
STRIPE_SECRET_KEY=sk_test_... oder sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_test_... oder pk_live_...

# STRIPE PRICE-IDs (aus Stripe Dashboard kopieren)
STRIPE_PRICE_SMALL_ID=price_1234567890abcdef      # z.B. 100 Credits
STRIPE_PRICE_MEDIUM_ID=price_abcdef1234567890     # z.B. 500 Credits  
STRIPE_PRICE_LARGE_ID=price_fedcba0987654321      # z.B. 1000 Credits

# STRIPE SUCCESS/CANCEL URLs
STRIPE_SUCCESS_URL=https://gojob.ing/dashboard?payment=success
STRIPE_CANCEL_URL=https://gojob.ing/pricing?payment=cancelled

# DATABASE & AUTH
DATABASE_URL=postgresql://...
NEXTAUTH_SECRET=your_secret_here
NEXTAUTH_URL=https://gojob.ing

# LOGGING & DEBUGGING
STRIPE_WEBHOOK_DEBUG=true
CREDITS_DEBUG=true

# =====================================================
# WICHTIGE HINWEISE:
# 1. Alle STRIPE_* Variablen sind erforderlich
# 2. Price-IDs aus Stripe Dashboard kopieren (Products > Pricing)
# 3. Webhook-Secret aus Stripe Dashboard (Webhooks > Endpoint)
# 4. In Render: Dashboard > Service > Environment
# 5. Lokal: .env Datei im Backend-Verzeichnis
'''
            
            env_file = self.project_root / "STRIPE_ENVIRONMENT_TEMPLATE.env"
            env_file.write_text(env_template, encoding='utf-8')
            
            self.log("SUCCESS", f"Environment Template erstellt: {env_file}")
            self.fixes_applied.append("Environment Variables Template erstellt")
            return True
            
        except Exception as e:
            self.log("ERROR", "Environment Template Erstellung fehlgeschlagen", str(e))
            self.fixes_failed.append(f"Environment Template: {str(e)}")
            return False
    
    def create_webhook_debugging_endpoint(self) -> bool:
        """Fix 4: Webhook Debugging Endpoint"""
        self.log("FIX", "Fix 4: Webhook Debugging Endpoint")
        
        try:
            debug_endpoint = '''
# STRIPE WEBHOOK DEBUG ENDPOINT
# Fügen Sie diese Route zu webhooks.py hinzu für besseres Debugging

@router.post("/stripe/debug")
async def debug_stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Debug-Endpoint für Stripe Webhook Probleme"""
    
    try:
        body = await request.body()
        stripe_signature = request.headers.get("stripe-signature", "")
        
        # Log raw webhook data
        logger.info(f"🔍 Debug Webhook Raw Body: {body[:500]}...")
        logger.info(f"🔍 Debug Webhook Headers: {dict(request.headers)}")
        
        # Try to parse as Stripe event
        try:
            event = stripe.Webhook.construct_event(
                body, stripe_signature, os.getenv("STRIPE_WEBHOOK_SECRET")
            )
            logger.info(f"✅ Debug Webhook Event Type: {event['type']}")
            logger.info(f"✅ Debug Webhook Event Data: {json.dumps(event['data'], indent=2)}")
            
            # If checkout.session.completed, test user resolution
            if event["type"] == "checkout.session.completed":
                session_obj = event["data"]["object"]
                
                # Test user resolution
                webhook_service = StripeWebhookService(db)
                user_id = await webhook_service._resolve_user_id(session_obj)
                
                return {
                    "debug_status": "success",
                    "event_type": event["type"],
                    "user_id_resolved": user_id,
                    "metadata": session_obj.get("metadata", {}),
                    "customer": session_obj.get("customer"),
                    "session_id": session_obj.get("id")
                }
            
        except Exception as e:
            logger.error(f"❌ Debug Webhook Parse Error: {e}")
            return {
                "debug_status": "parse_error",
                "error": str(e),
                "raw_body_length": len(body),
                "headers": dict(request.headers)
            }
            
    except Exception as e:
        logger.error(f"❌ Debug Webhook Critical Error: {e}")
        return {"debug_status": "critical_error", "error": str(e)}
'''
            
            debug_file = self.project_root / "webhook_debug_endpoint.py"
            debug_file.write_text(debug_endpoint, encoding='utf-8')
            
            self.log("SUCCESS", f"Webhook Debug Endpoint erstellt: {debug_file}")
            self.fixes_applied.append("Webhook Debug Endpoint erstellt")
            return True
            
        except Exception as e:
            self.log("ERROR", "Webhook Debug Endpoint Erstellung fehlgeschlagen", str(e))
            self.fixes_failed.append(f"Debug Endpoint: {str(e)}")
            return False
    
    def create_testing_script(self) -> bool:
        """Fix 5: Automatischer Testing Script"""
        self.log("FIX", "Fix 5: Automatischer Testing Script")
        
        try:
            test_script = '''#!/usr/bin/env python3
"""
🧪 AUTOMATISCHER STRIPE CREDITS TEST
===================================
Testet die komplette Credits-Pipeline nach den Fixes
"""

import requests
import json
import time
from datetime import datetime

def test_complete_credits_flow():
    """Testet den kompletten Credits-Flow"""
    
    print("🧪 AUTOMATISCHER STRIPE CREDITS TEST")
    print("="*50)
    
    # Test 1: Environment Check
    print("\\n1. Environment Check...")
    response = requests.get("https://resume-matcher-backend-j06k.onrender.com/health")
    if response.status_code == 200:
        print("✅ Backend erreichbar")
    else:
        print("❌ Backend nicht erreichbar")
    
    # Test 2: Webhook Debug
    print("\\n2. Webhook Debug Test...")
    test_webhook = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": None,
                "metadata": {
                    "user_id": "test_user_123",
                    "credits": "100",
                    "price_id": "price_test"
                }
            }
        }
    }
    
    try:
        response = requests.post(
            "https://resume-matcher-backend-j06k.onrender.com/webhooks/stripe/debug",
            json=test_webhook,
            headers={"Stripe-Signature": "t=1693906800,v1=test_signature"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook Debug Response: {result}")
            
            if result.get("user_id_resolved"):
                print("✅ User-ID Resolution funktioniert!")
            else:
                print("❌ User-ID Resolution fehlgeschlagen")
        else:
            print(f"⚠️ Webhook Debug Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Webhook Debug Error: {e}")
    
    # Test 3: Authentication Check
    print("\\n3. Authentication Check...")
    response = requests.post(
        "https://gojob.ing/api/stripe/checkout",
        json={"price_id": "price_test"},
        timeout=10
    )
    
    if response.status_code == 401:
        print("✅ Checkout Authentication funktioniert")
    else:
        print(f"⚠️ Checkout Authentication Status: {response.status_code}")
    
    print("\\n🎯 TEST ABGESCHLOSSEN")
    print("Führen Sie nun einen echten Test-Kauf durch!")

if __name__ == "__main__":
    test_complete_credits_flow()
'''
            
            test_file = self.project_root / "test_stripe_credits_fixed.py"
            test_file.write_text(test_script, encoding='utf-8')
            
            self.log("SUCCESS", f"Testing Script erstellt: {test_file}")
            self.fixes_applied.append("Automatischer Testing Script erstellt")
            return True
            
        except Exception as e:
            self.log("ERROR", "Testing Script Erstellung fehlgeschlagen", str(e))
            self.fixes_failed.append(f"Testing Script: {str(e)}")
            return False
    
    def apply_all_fixes(self):
        """Hauptfunktion: Alle Fixes anwenden"""
        print("🔧 AUTOMATISCHES STRIPE CREDITS FIX-TOOL")
        print("="*60)
        print(f"Projekt: {self.project_root}")
        print(f"Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Alle Fixes nacheinander anwenden
        fixes = [
            ("Checkout Metadata", self.fix_checkout_metadata),
            ("Webhook User Resolution", self.fix_webhook_user_resolution),
            ("Environment Template", self.create_environment_template),
            ("Webhook Debug Endpoint", self.create_webhook_debugging_endpoint),
            ("Testing Script", self.create_testing_script)
        ]
        
        for fix_name, fix_function in fixes:
            self.log("INFO", f"Anwenden: {fix_name}")
            try:
                success = fix_function()
                if success:
                    self.log("SUCCESS", f"✅ {fix_name} erfolgreich")
                else:
                    self.log("WARNING", f"⚠️ {fix_name} teilweise erfolgreich")
            except Exception as e:
                self.log("ERROR", f"❌ {fix_name} fehlgeschlagen", str(e))
                self.fixes_failed.append(f"{fix_name}: {str(e)}")
            print()
        
        # Zusammenfassung
        print("🎯 FIX-ZUSAMMENFASSUNG")
        print("="*40)
        
        if self.fixes_applied:
            print("✅ ERFOLGREICH ANGEWENDET:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        if self.fixes_failed:
            print("\\n❌ FEHLGESCHLAGEN:")
            for fix in self.fixes_failed:
                print(f"   • {fix}")
        
        print("\\n🚀 NÄCHSTE SCHRITTE:")
        print("   1. Führen Sie 'python test_stripe_credits_fixed.py' aus")
        print("   2. Setzen Sie die Environment Variables aus STRIPE_ENVIRONMENT_TEMPLATE.env")
        print("   3. Testen Sie einen echten Kauf")
        print("   4. Überprüfen Sie die Webhook-Logs")

if __name__ == "__main__":
    fix_tool = StripeCreditsAutofix()
    fix_tool.apply_all_fixes()
