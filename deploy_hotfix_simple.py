#!/usr/bin/env python3
"""
🚀 SIMPLE HOTFIX DEPLOYMENT

Simplified deployment script that applies the hotfix without requiring Alembic.
Directly executes SQL commands to set up the database schema.

Usage:
    python deploy_hotfix_simple.py [--dry-run]
"""

import argparse
import asyncio
import logging
import sys
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def setup_database_schema():
    """Set up database schema directly without Alembic."""
    logger.info("🔧 Setting up database schema...")
    
    try:
        # Add backend to Python path
        backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
        if os.path.exists(backend_path):
            sys.path.insert(0, backend_path)
        
        from app.core.database import get_async_session_local
        from sqlalchemy import text
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            logger.info("🔍 Checking existing schema...")
            
            # 1. Check and create stripe_events table
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables
                WHERE table_name='stripe_events'
            """))
            
            if not result.fetchone():
                logger.info("🔧 Creating stripe_events table...")
                
                await session.execute(text("""
                    CREATE TABLE stripe_events (
                        event_id VARCHAR(255) NOT NULL,
                        event_type VARCHAR(100) NOT NULL,
                        processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        raw_data JSONB,
                        processing_status VARCHAR(50) NOT NULL DEFAULT 'completed',
                        error_message TEXT,
                        PRIMARY KEY (event_id)
                    )
                """))
                
                await session.execute(text("""
                    CREATE INDEX ix_stripe_events_event_id ON stripe_events (event_id)
                """))
                
                await session.execute(text("""
                    CREATE INDEX ix_stripe_events_event_type ON stripe_events (event_type)
                """))
                
                logger.info("✅ stripe_events table created")
            else:
                logger.info("✅ stripe_events table already exists")
            
            # 2. Check and add credits_balance column
            result = await session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns
                WHERE table_name='users' AND column_name='credits_balance'
            """))
            
            if not result.fetchone():
                logger.info("🔧 Adding credits_balance column...")
                await session.execute(text("""
                    ALTER TABLE users ADD COLUMN credits_balance INTEGER NOT NULL DEFAULT 0
                """))
                logger.info("✅ credits_balance column added")
            else:
                logger.info("✅ credits_balance column already exists")
            
            # 3. Add constraints (if they don't exist)
            logger.info("🔧 Adding constraints and indexes...")
            
            # Check for constraint
            result = await session.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints
                WHERE table_name='users' AND constraint_name='credits_balance_nonneg'
            """))
            
            if not result.fetchone():
                try:
                    await session.execute(text("""
                        ALTER TABLE users ADD CONSTRAINT credits_balance_nonneg CHECK (credits_balance >= 0)
                    """))
                    logger.info("✅ credits_balance constraint added")
                except Exception as e:
                    logger.warning(f"⚠️  Constraint might already exist: {e}")
            else:
                logger.info("✅ credits_balance constraint already exists")
            
            # 4. Add email index
            try:
                await session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)
                """))
                logger.info("✅ email index ensured")
            except Exception as e:
                logger.warning(f"⚠️  Email index issue: {e}")
            
            # Commit all changes
            await session.commit()
            logger.info("✅ Database schema setup completed")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False


async def verify_hotfix_components():
    """Verify that hotfix components can be imported."""
    logger.info("🧪 Verifying hotfix components...")
    
    try:
        # Test imports
        from app.db.session_patterns import run_in_tx, safe_commit
        from app.db.resolver_fix import find_user, resolve_user, is_email
        from app.models.stripe_event import StripeEvent
        from app.webhooks.stripe_checkout_completed_hotfix import handle_checkout_completed
        from app.api.router.webhooks_hotfix import webhooks_hotfix_router
        
        # Test validation functions
        assert is_email("test@example.com") == True
        assert is_email("invalid") == False
        
        logger.info("✅ All hotfix components verified")
        return True
        
    except Exception as e:
        logger.error(f"❌ Component verification failed: {e}")
        return False


async def test_database_operations():
    """Test basic database operations with the hotfix."""
    logger.info("🔬 Testing database operations...")
    
    try:
        from app.core.database import get_async_session_local
        from app.models.user import User
        from app.db.resolver_fix import find_user
        from sqlalchemy import text
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            # Test finding a user (should not crash)
            user = await find_user(session, User, "test@example.com")
            # Should return None for non-existent user
            
            # Test credits_balance query
            result = await session.execute(text("""
                SELECT COUNT(*) as user_count,
                       COALESCE(SUM(credits_balance), 0) as total_credits
                FROM users
            """))
            stats = result.fetchone()
            logger.info(f"📊 Database stats: {stats.user_count} users, {stats.total_credits} total credits")
            
            # Test stripe_events table
            result = await session.execute(text("""
                SELECT COUNT(*) as event_count FROM stripe_events
            """))
            event_count = result.scalar()
            logger.info(f"📊 Stripe events: {event_count} events processed")
            
        logger.info("✅ Database operations test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database operations test failed: {e}")
        return False


async def deploy_simple_hotfix(dry_run: bool = False):
    """Deploy the hotfix using simple approach."""
    logger.info("🚀 Starting simple hotfix deployment...")
    
    if dry_run:
        logger.info("🏃 DRY RUN MODE - No actual changes will be made")
    
    # Add backend to Python path
    backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
    
    steps = []
    
    # Step 1: Database schema setup
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Database Schema Setup")
    logger.info("="*60)
    
    if not dry_run:
        schema_success = await setup_database_schema()
    else:
        logger.info("🏃 DRY RUN: Would set up database schema")
        schema_success = True
    
    steps.append(("Database Schema", schema_success))
    
    if not schema_success:
        logger.error("❌ Database schema setup failed")
        return False
    
    # Step 2: Component verification
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Component Verification")
    logger.info("="*60)
    
    component_success = await verify_hotfix_components()
    steps.append(("Component Verification", component_success))
    
    if not component_success:
        logger.error("❌ Component verification failed")
        return False
    
    # Step 3: Database operations test
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Database Operations Test")
    logger.info("="*60)
    
    if not dry_run:
        db_test_success = await test_database_operations()
    else:
        logger.info("🏃 DRY RUN: Would test database operations")
        db_test_success = True
    
    steps.append(("Database Operations", db_test_success))
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("🏁 SIMPLE HOTFIX DEPLOYMENT SUMMARY")
    logger.info("="*60)
    
    for step_name, result in steps:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {step_name}")
    
    failed_steps = [name for name, result in steps if result is False]
    
    if not failed_steps:
        logger.info("\n🎉 SIMPLE HOTFIX DEPLOYMENT SUCCESSFUL!")
        logger.info("✅ Ready to use the hotfix components")
        logger.info("\n📋 Available endpoints:")
        logger.info("- POST /webhooks/stripe/hotfix")
        logger.info("- POST /api/stripe/webhook/hotfix (legacy)")
        logger.info("\n🧪 Test with:")
        logger.info("python hotfix_verification_test.py")
        return True
    else:
        logger.error(f"\n❌ SIMPLE HOTFIX DEPLOYMENT FAILED!")
        logger.error(f"Failed steps: {', '.join(failed_steps)}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy hotfix with simple approach")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying them")
    
    args = parser.parse_args()
    
    try:
        success = asyncio.run(deploy_simple_hotfix(args.dry_run))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Deployment crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
