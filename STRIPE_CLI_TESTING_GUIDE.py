#!/usr/bin/env python3
"""
🎯 STRIPE CLI TESTING GUIDE
===========================

Guide for testing the Ultimate Stripe Webhook Fix using real Stripe CLI commands.
This provides the most accurate testing as it uses actual Stripe webhook signatures.

Prerequisites:
- Stripe CLI installed: https://stripe.com/docs/stripe-cli#install
- Stripe account access with webhook secret

Use this for final validation of the Ultimate Webhook Fix.
"""

import subprocess
import time
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "https://resume-matcher-backend-j06k.onrender.com"
TEST_USER_ID = "e747de39-1b54-4cd0-96eb-e68f155931e2"


def print_banner():
    """Print testing banner"""
    logger.info("🎯 STRIPE CLI TESTING GUIDE FOR ULTIMATE WEBHOOK FIX")
    logger.info("=" * 60)
    logger.info("This guide helps you test the Ultimate Stripe Webhook Fix")
    logger.info("using real Stripe CLI commands with proper signatures.")
    logger.info("=" * 60)


def check_stripe_cli():
    """Check if Stripe CLI is installed"""
    try:
        result = subprocess.run(['stripe', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Stripe CLI installed: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ Stripe CLI not found")
            return False
    except FileNotFoundError:
        logger.error("❌ Stripe CLI not found")
        return False


def print_setup_instructions():
    """Print setup instructions"""
    logger.info("\n📋 SETUP INSTRUCTIONS:")
    logger.info("=" * 40)
    logger.info("1. Install Stripe CLI:")
    logger.info("   https://stripe.com/docs/stripe-cli#install")
    logger.info("")
    logger.info("2. Login to Stripe:")
    logger.info("   stripe login")
    logger.info("")
    logger.info("3. Get your webhook secret from Stripe Dashboard:")
    logger.info("   https://dashboard.stripe.com/webhooks")
    logger.info("")
    logger.info("4. Set environment variable:")
    logger.info("   export STRIPE_WEBHOOK_SECRET=whsec_...")
    logger.info("")


def print_testing_commands():
    """Print the testing commands"""
    logger.info("\n🧪 ULTIMATE WEBHOOK FIX TESTING COMMANDS:")
    logger.info("=" * 50)
    
    logger.info("\n1. 🎯 BASIC WEBHOOK TEST:")
    logger.info("   Test the webhook endpoint with real Stripe signature:")
    logger.info("")
    logger.info(f"   stripe listen --forward-to {BACKEND_URL}/")
    logger.info("")
    logger.info("   ✅ Expected: 'Ready! You are using Stripe API Version...'")
    logger.info("   ✅ Keep this running and proceed to next step")
    
    logger.info("\n2. 🚀 TRIGGER CHECKOUT SESSION COMPLETED:")
    logger.info("   In a new terminal, trigger the specific event we handle:")
    logger.info("")
    cmd = f"   stripe trigger checkout.session.completed \\\n     --add checkout_session:metadata[user_id]={TEST_USER_ID} \\\n     --add checkout_session:metadata[credits]=100"
    logger.info(cmd)
    logger.info("")
    logger.info("   ✅ Expected in listener terminal:")
    logger.info("   '2023-XX-XX XX:XX:XX   --> checkout.session.completed [evt_...]'")
    logger.info("   '2023-XX-XX XX:XX:XX  <--  [200] POST http://localhost:...'")
    
    logger.info("\n3. 🔍 ADVANCED TESTING:")
    logger.info("   Test different credit amounts:")
    logger.info("")
    
    scenarios = [
        ("Small Payment", 10),
        ("Medium Payment", 100),
        ("Large Payment", 500)
    ]
    
    for name, credits in scenarios:
        logger.info(f"   # {name} ({credits} credits)")
        cmd = f"   stripe trigger checkout.session.completed \\\n     --add checkout_session:metadata[user_id]={TEST_USER_ID} \\\n     --add checkout_session:metadata[credits]={credits}"
        logger.info(cmd)
        logger.info("")
    
    logger.info("4. 🚨 ERROR TESTING:")
    logger.info("   Test error scenarios:")
    logger.info("")
    logger.info("   # Missing user_id (should fail gracefully)")
    logger.info("   stripe trigger checkout.session.completed \\")
    logger.info("     --add checkout_session:metadata[credits]=100")
    logger.info("")
    logger.info("   # Missing credits (should fail gracefully)")
    logger.info(f"   stripe trigger checkout.session.completed \\")
    logger.info(f"     --add checkout_session:metadata[user_id]={TEST_USER_ID}")
    logger.info("")


def print_success_indicators():
    """Print what to look for to confirm success"""
    logger.info("\n🎉 SUCCESS INDICATORS:")
    logger.info("=" * 30)
    logger.info("✅ Stripe CLI listener shows:")
    logger.info("   --> checkout.session.completed [evt_...]")
    logger.info("   <-- [200] POST https://resume-matcher-backend-j06k.onrender.com/")
    logger.info("")
    logger.info("✅ Backend logs should show:")
    logger.info("   ✅ Stripe signature verified for event: evt_...")
    logger.info("   🔍 Processing checkout.session.completed:")
    logger.info("   ✅ User-ID from metadata: e747de39-1b54-4cd0-96eb-e68f155931e2")
    logger.info("   🎉 SUCCESS: 100 credits added to user e747de39-1b54-4cd0-96eb-e68f155931e2")
    logger.info("")
    logger.info("✅ Database should show:")
    logger.info("   User credit balance increased by the specified amount")


def print_troubleshooting():
    """Print troubleshooting guide"""
    logger.info("\n🔧 TROUBLESHOOTING:")
    logger.info("=" * 20)
    logger.info("❌ If you see 'Invalid payload':")
    logger.info("   Check that STRIPE_WEBHOOK_SECRET is set correctly")
    logger.info("")
    logger.info("❌ If you see '404 Not found':")
    logger.info("   Check the User-Agent header (should be 'Stripe/1.0')")
    logger.info("")
    logger.info("❌ If you see 'no_user_mapping':")
    logger.info("   Check that user_id is included in metadata")
    logger.info("")
    logger.info("❌ If you see 'no_credits':")
    logger.info("   Check that credits field is included in metadata")
    logger.info("")
    logger.info("❌ If credits don't appear in database:")
    logger.info("   Check backend logs for database transaction errors")


def print_monitoring_commands():
    """Print monitoring commands"""
    logger.info("\n📊 MONITORING COMMANDS:")
    logger.info("=" * 25)
    logger.info("# Run these in separate terminals while testing:")
    logger.info("")
    logger.info("# Real-time webhook monitoring")
    logger.info("python STRIPE_WEBHOOK_MONITOR.py")
    logger.info("")
    logger.info("# Direct webhook testing (without Stripe CLI)")
    logger.info("python DIRECT_STRIPE_WEBHOOK_TEST.py")
    logger.info("")
    logger.info("# Check backend health")
    logger.info(f"curl {BACKEND_URL}/ping")


def main():
    """Main function"""
    print_banner()
    
    # Check if Stripe CLI is available
    cli_available = check_stripe_cli()
    
    if not cli_available:
        print_setup_instructions()
    
    print_testing_commands()
    print_success_indicators()
    print_troubleshooting()
    print_monitoring_commands()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 ULTIMATE STRIPE WEBHOOK FIX - TESTING COMPLETE")
    logger.info("=" * 60)
    logger.info("Use the commands above to validate the webhook implementation")
    logger.info("with real Stripe signatures and events.")
    logger.info("")
    logger.info("The Ultimate Webhook Fix should handle all scenarios correctly!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
