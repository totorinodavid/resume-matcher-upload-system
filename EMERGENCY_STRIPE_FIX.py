#!/usr/bin/env python3
"""
🚨 EMERGENCY STRIPE PACKAGE FIX
===============================

Emergency script to diagnose and fix the Stripe package installation issue
that's causing webhook failures in production.

This script:
1. Checks if Stripe package is installed
2. Validates the installation
3. Provides deployment commands to fix the issue
4. Tests the webhook functionality

Run this immediately to resolve the production webhook failure.
"""

import subprocess
import sys
import logging
import importlib.util

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_stripe_installation():
    """Check if Stripe package is properly installed"""
    logger.info("🔍 Checking Stripe package installation...")
    
    try:
        import stripe
        logger.info(f"✅ Stripe package imported successfully")
        logger.info(f"   Version: {stripe.__version__}")
        logger.info(f"   Location: {stripe.__file__}")
        return True
    except ImportError as e:
        logger.error(f"❌ Stripe package import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error importing Stripe: {e}")
        return False


def check_package_in_requirements():
    """Check if Stripe is listed in pyproject.toml"""
    logger.info("📋 Checking pyproject.toml for Stripe dependency...")
    
    try:
        with open("apps/backend/pyproject.toml", "r") as f:
            content = f.read()
            
        if "stripe" in content.lower():
            logger.info("✅ Stripe dependency found in pyproject.toml")
            # Extract the stripe line
            for line in content.split('\n'):
                if 'stripe' in line.lower() and '=' in line:
                    logger.info(f"   Dependency: {line.strip()}")
            return True
        else:
            logger.error("❌ Stripe dependency NOT found in pyproject.toml")
            return False
    except FileNotFoundError:
        logger.error("❌ pyproject.toml not found")
        return False
    except Exception as e:
        logger.error(f"❌ Error reading pyproject.toml: {e}")
        return False


def test_stripe_functionality():
    """Test basic Stripe functionality"""
    logger.info("🧪 Testing Stripe functionality...")
    
    try:
        import stripe
        
        # Test basic Stripe operations
        logger.info("   Testing Stripe.Webhook class...")
        webhook_class = stripe.Webhook
        logger.info(f"   ✅ Stripe.Webhook available: {webhook_class}")
        
        logger.info("   Testing construct_event method...")
        construct_method = getattr(webhook_class, 'construct_event', None)
        if construct_method:
            logger.info("   ✅ construct_event method available")
        else:
            logger.error("   ❌ construct_event method not found")
            return False
            
        logger.info("✅ Stripe functionality test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Stripe functionality test failed: {e}")
        return False


def check_python_environment():
    """Check Python environment details"""
    logger.info("🐍 Checking Python environment...")
    
    logger.info(f"   Python version: {sys.version}")
    logger.info(f"   Python executable: {sys.executable}")
    logger.info(f"   Python path: {sys.path[:3]}...")  # Show first 3 paths


def provide_deployment_fix():
    """Provide deployment fix commands"""
    logger.info("\n🔧 DEPLOYMENT FIX COMMANDS:")
    logger.info("=" * 50)
    
    logger.info("1. 🚀 IMMEDIATE FIX - Render Deployment:")
    logger.info("   If using Render, trigger a new deployment:")
    logger.info("   • Go to Render Dashboard")
    logger.info("   • Click 'Manual Deploy' → 'Clear build cache & deploy'")
    logger.info("   • This will reinstall all dependencies from pyproject.toml")
    logger.info("")
    
    logger.info("2. 🔧 MANUAL PACKAGE INSTALLATION:")
    logger.info("   If you have access to the production environment:")
    logger.info("   pip install stripe>=7.0.0")
    logger.info("   # or")
    logger.info("   pip install -e .")
    logger.info("")
    
    logger.info("3. 🚨 EMERGENCY WEBHOOK MODE:")
    logger.info("   Set environment variable to bypass signature verification:")
    logger.info("   ALLOW_UNVERIFIED_WEBHOOKS=1")
    logger.info("   ⚠️ WARNING: This is INSECURE and should only be temporary!")
    logger.info("")
    
    logger.info("4. 📦 DEPENDENCY VERIFICATION:")
    logger.info("   Ensure pyproject.toml has the correct Stripe dependency:")
    logger.info('   "stripe>=7.0.0,<8.0.0",')
    logger.info("")
    
    logger.info("5. 🧪 VERIFY FIX:")
    logger.info("   After deployment, run:")
    logger.info("   python EMERGENCY_STRIPE_FIX.py")
    logger.info("   python DIRECT_STRIPE_WEBHOOK_TEST.py")


def check_environment_variables():
    """Check required environment variables"""
    logger.info("🌍 Checking environment variables...")
    
    import os
    
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    api_key = os.getenv('STRIPE_SECRET_KEY')
    
    if webhook_secret:
        logger.info(f"✅ STRIPE_WEBHOOK_SECRET configured (ends with: ...{webhook_secret[-4:]})")
    else:
        logger.error("❌ STRIPE_WEBHOOK_SECRET not configured")
    
    if api_key:
        logger.info(f"✅ STRIPE_SECRET_KEY configured (starts with: {api_key[:7]}...)")
    else:
        logger.warning("⚠️ STRIPE_SECRET_KEY not configured (may be optional)")


def main():
    """Main diagnostic function"""
    logger.info("🚨 EMERGENCY STRIPE PACKAGE DIAGNOSTIC")
    logger.info("=" * 50)
    logger.info("Diagnosing Stripe package installation issue causing webhook failures")
    logger.info("=" * 50)
    
    # Run all diagnostic checks
    stripe_installed = check_stripe_installation()
    requirements_ok = check_package_in_requirements()
    
    if stripe_installed:
        functionality_ok = test_stripe_functionality()
    else:
        functionality_ok = False
    
    check_python_environment()
    check_environment_variables()
    
    # Provide summary
    logger.info("\n" + "=" * 50)
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info("=" * 50)
    logger.info(f"   Stripe Package Installed: {'✅ YES' if stripe_installed else '❌ NO'}")
    logger.info(f"   Listed in Requirements: {'✅ YES' if requirements_ok else '❌ NO'}")
    logger.info(f"   Functionality Working: {'✅ YES' if functionality_ok else '❌ NO'}")
    
    if stripe_installed and functionality_ok:
        logger.info("\n🎉 STRIPE PACKAGE IS WORKING CORRECTLY!")
        logger.info("   The webhook failures may be due to other issues.")
        logger.info("   Check logs for signature verification or configuration problems.")
    else:
        logger.error("\n❌ STRIPE PACKAGE ISSUE CONFIRMED!")
        logger.error("   The webhook failures are due to missing/broken Stripe package.")
        provide_deployment_fix()
    
    # Return status for automation
    return stripe_installed and functionality_ok


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Diagnostic script failed: {e}")
        sys.exit(1)
