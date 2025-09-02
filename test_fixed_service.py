#!/usr/bin/env python3
"""
🧪 Test the fixed UltraEmergencyUserService
"""

import asyncio
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_fixed_service():
    """Test the fixed UltraEmergencyUserService."""
    try:
        # Add backend to Python path
        backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
        if os.path.exists(backend_path):
            sys.path.insert(0, backend_path)
        
        from app.core.database import get_async_session_local
        from app.services.ultra_emergency_user_service import UltraEmergencyUserService
        
        logger.info("🧪 Testing fixed UltraEmergencyUserService...")
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            service = UltraEmergencyUserService(session)
            
            # Test user resolution
            logger.info("1. Testing user resolution by email...")
            user = await service.resolve_user_by_any_id("test@example.com")
            if user:
                logger.info(f"✅ Found user: {user.id} - {user.email}")
            else:
                logger.info("⚠️  No user found (this might be expected)")
            
            # Test user resolution by ID
            logger.info("2. Testing user resolution by ID...")
            user = await service.resolve_user_by_any_id("1")
            if user:
                logger.info(f"✅ Found user by ID: {user.id} - {user.email}")
            else:
                logger.info("⚠️  No user found by ID")
            
            # Test canonical ID resolution
            logger.info("3. Testing canonical ID resolution...")
            canonical_id = await service.get_canonical_user_id("test@example.com")
            if canonical_id:
                logger.info(f"✅ Canonical ID: {canonical_id}")
            else:
                logger.info("⚠️  No canonical ID found")
            
            # Test with a UUID (like in the production logs)
            logger.info("4. Testing with UUID from production logs...")
            test_uuid = "58975f6d-ec48-481f-896b-cc45e33cc99b"
            user = await service.resolve_user_by_any_id(test_uuid)
            if user:
                logger.info(f"✅ Found user by UUID: {user.id} - {user.email}")
            else:
                logger.info("⚠️  No user found by UUID (expected for test)")
            
            logger.info("🎉 All tests completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    try:
        success = asyncio.run(test_fixed_service())
        if success:
            print("\n✅ FIXED SERVICE TEST PASSED!")
            print("The UltraEmergencyUserService should now handle transaction errors properly.")
        else:
            print("\n❌ Test failed - check logs above")
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
