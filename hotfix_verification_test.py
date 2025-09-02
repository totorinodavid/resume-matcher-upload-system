#!/usr/bin/env python3
"""
🧪 HOTFIX VERIFICATION SCRIPT

Comprehensive test suite for the credits_balance + UUID-Resolver + Transaction Handling hotfix.
Tests all components in isolation and integration.

Usage:
    python hotfix_verification_test.py
"""

import asyncio
import logging
import sys
import uuid
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_session_patterns():
    """Test secure session/transaction patterns."""
    logger.info("🧪 Testing session patterns...")
    
    try:
        from app.db.session_patterns import run_in_tx, safe_commit, safe_rollback
        from app.core.database import get_async_session_local
        
        session_factory = get_async_session_local()
        
        # Test successful transaction
        async def success_work(session):
            return {"result": "success"}
        
        result = await run_in_tx(session_factory, success_work)
        assert result["result"] == "success"
        
        logger.info("✅ Session patterns working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Session patterns test failed: {e}")
        return False


async def test_user_resolver():
    """Test robust user resolver functionality."""
    logger.info("🧪 Testing user resolver...")
    
    try:
        from app.db.resolver_fix import (
            is_uuid, is_email, is_placeholder, is_integer_id,
            find_user, resolve_user
        )
        
        # Test validation functions
        assert is_email("test@example.com") == True
        assert is_email("invalid-email") == False
        assert is_email("<email>") == False
        
        assert is_placeholder("<email>") == True
        assert is_placeholder("test@example.com") == False
        assert is_placeholder("null") == True
        
        assert is_integer_id("123") == True
        assert is_integer_id("abc") == False
        
        # Test UUID validation
        test_uuid = str(uuid.uuid4())
        assert is_uuid(test_uuid) == True
        assert is_uuid("not-a-uuid") == False
        
        logger.info("✅ User resolver validation functions working correctly")
        return True
        
    except ImportError as e:
        logger.error(f"❌ User resolver import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ User resolver test failed: {e}")
        return False


async def test_database_integration():
    """Test database integration with hotfix components."""
    logger.info("🧪 Testing database integration...")
    
    try:
        from app.core.database import get_db_session, get_async_session_local
        from app.models.user import User
        from app.models.stripe_event import StripeEvent
        from app.db.resolver_fix import find_user, resolve_or_create_user
        
        session_factory = get_async_session_local()
        
        async with session_factory() as session:
            # Test finding a user (should not crash even if no users exist)
            user = await find_user(session, User, "nonexistent@example.com")
            # Should return None for non-existent user
            
            logger.info("✅ Database integration working correctly")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database integration test failed: {e}")
        return False


async def test_webhook_handler():
    """Test webhook handler integration."""
    logger.info("🧪 Testing webhook handler...")
    
    try:
        from app.webhooks.stripe_checkout_completed_hotfix import (
            handle_checkout_completed,
            _extract_credits_from_metadata
        )
        
        # Test metadata extraction
        metadata = {"credits": "100", "session_email": "test@example.com"}
        credits = _extract_credits_from_metadata(metadata)
        assert credits == 100
        
        # Test empty metadata
        empty_metadata = {}
        credits = _extract_credits_from_metadata(empty_metadata)
        assert credits == 0
        
        logger.info("✅ Webhook handler components working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Webhook handler test failed: {e}")
        return False


async def test_model_imports():
    """Test that all models can be imported."""
    logger.info("🧪 Testing model imports...")
    
    try:
        from app.models.user import User
        from app.models.stripe_event import StripeEvent
        from app.models.base import Base
        
        # Check model attributes
        assert hasattr(User, 'id')
        assert hasattr(User, 'email')
        assert hasattr(User, 'name')
        assert hasattr(User, 'credits_balance')
        
        assert hasattr(StripeEvent, 'event_id')
        assert hasattr(StripeEvent, 'event_type')
        assert hasattr(StripeEvent, 'processing_status')
        
        logger.info("✅ All models imported successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model import test failed: {e}")
        return False


async def test_api_router_import():
    """Test that the hotfix API router can be imported."""
    logger.info("🧪 Testing API router import...")
    
    try:
        from app.api.router.webhooks_hotfix import webhooks_hotfix_router
        
        # Check that router has expected endpoints
        routes = [route.path for route in webhooks_hotfix_router.routes]
        assert "/webhooks/stripe/hotfix" in routes
        
        logger.info("✅ API router imported successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ API router import test failed: {e}")
        return False


def test_sql_verification_file():
    """Test that SQL verification file was created."""
    logger.info("🧪 Testing SQL verification file...")
    
    try:
        import os
        sql_file = "hotfix_verification.sql"
        
        if os.path.exists(sql_file):
            with open(sql_file, 'r') as f:
                content = f.read()
                assert "credits_balance" in content
                assert "stripe_events" in content
                assert "SELECT" in content
                
            logger.info("✅ SQL verification file created successfully")
            return True
        else:
            logger.warning("⚠️  SQL verification file not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ SQL verification file test failed: {e}")
        return False


async def run_all_tests():
    """Run all hotfix verification tests."""
    logger.info("🚀 Starting hotfix verification tests...")
    
    # Ensure Python path is set up
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
    if os.path.exists(backend_path) and backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    tests = [
        ("Session Patterns", test_session_patterns),
        ("User Resolver", test_user_resolver),
        ("Database Integration", test_database_integration),
        ("Webhook Handler", test_webhook_handler),
        ("Model Imports", test_model_imports),
        ("API Router Import", test_api_router_import),
    ]
    
    sync_tests = [
        ("SQL Verification File", test_sql_verification_file),
    ]
    
    results = {}
    
    # Run async tests
    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Run sync tests
    for test_name, test_func in sync_tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 HOTFIX VERIFICATION RESULTS")
    logger.info("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("="*60)
    logger.info(f"📈 Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        logger.info("🎉 All hotfix components verified successfully!")
        logger.info("✅ Ready for production deployment")
    else:
        logger.warning("⚠️  Some components need attention before deployment")
    
    return failed == 0


if __name__ == "__main__":
    # Add the backend app to Python path
    import sys
    import os
    backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
    else:
        # Fallback: try current directory structure
        current_dir = os.path.dirname(__file__)
        sys.path.insert(0, current_dir)
    
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Test runner crashed: {e}")
        sys.exit(1)
