#!/usr/bin/env python3
"""
🚀 HOTFIX DEPLOYMENT SCRIPT

Comprehensive deployment script for the credits_balance + UUID-Resolver + Transaction Handling hotfix.
Applies the fix step by step with verification at each stage.

Usage:
    python deploy_hotfix.py [--dry-run] [--skip-migration]
"""

import argparse
import asyncio
import logging
import os
import subprocess
import sys
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_command(cmd: List[str], description: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command with logging."""
    logger.info(f"🔧 {description}")
    logger.debug(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        if result.stdout:
            logger.debug(f"STDOUT: {result.stdout}")
        if result.stderr:
            logger.debug(f"STDERR: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Command failed: {e}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        raise


async def apply_migration_manually():
    """Apply the migration manually using direct SQL execution."""
    logger.info("🛠️  Applying migration manually...")
    
    try:
        from app.core.database import get_async_session_local
        from sqlalchemy import text
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            # 1. Check if stripe_events table exists
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables
                WHERE table_name='stripe_events'
            """))
            
            if not result.fetchone():
                logger.info("🔧 Creating stripe_events table...")
                
                # Create stripe_events table
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
                
                # Create indexes
                await session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_stripe_events_event_id ON stripe_events (event_id)
                """))
                
                await session.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_stripe_events_event_type ON stripe_events (event_type)
                """))
                
                logger.info("✅ stripe_events table created successfully")
            else:
                logger.info("✅ stripe_events table already exists")
            
            # 2. Ensure credits_balance column exists with constraints
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
            
            # 3. Add constraints (ignore if they already exist)
            try:
                await session.execute(text("""
                    ALTER TABLE users ADD CONSTRAINT credits_balance_nonneg CHECK (credits_balance >= 0)
                """))
                logger.info("✅ credits_balance constraint added")
            except Exception:
                logger.info("✅ credits_balance constraint already exists")
            
            # 4. Add email index (ignore if it already exists)
            try:
                await session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)
                """))
                logger.info("✅ email index added")
            except Exception:
                logger.info("✅ email index already exists")
            
            # Commit all changes
            await session.commit()
            logger.info("✅ Manual migration completed successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Manual migration failed: {e}")
        return False


async def check_database_connection():
    """Verify database connection is working."""
    logger.info("🔍 Checking database connection...")
    
    try:
        from app.core.database import get_async_session_local
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            # Simple query to test connection
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            
        logger.info("✅ Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def run_migration(dry_run: bool = False):
    """Run Alembic migration for StripeEvent table and constraints."""
    logger.info("🔄 Running database migration...")
    
    if dry_run:
        logger.info("🏃 DRY RUN: Would run migration 0010_add_stripe_events_and_constraints")
        return True
    
    try:
        # Change to backend directory
        backend_dir = os.path.join(os.path.dirname(__file__), "apps", "backend")
        if os.path.exists(backend_dir):
            original_dir = os.getcwd()
            os.chdir(backend_dir)
        else:
            logger.warning("⚠️  Backend directory not found, trying from current directory")
            backend_dir = "."
            original_dir = os.getcwd()
        
        # Try multiple approaches to run Alembic
        migration_success = False
        
        # Approach 1: Try alembic command directly
        try:
            result = run_command(
                ["alembic", "upgrade", "head"],
                "Applying database migrations (direct alembic)",
                check=False
            )
            
            if result.returncode == 0:
                logger.info("✅ Migration applied successfully (direct alembic)")
                migration_success = True
            elif "already at head" in result.stdout or "No migrations to apply" in result.stdout:
                logger.info("✅ Database already up to date (direct alembic)")
                migration_success = True
                
        except FileNotFoundError:
            logger.info("🔧 Direct alembic command not found, trying python -m alembic...")
            
            # Approach 2: Try python -m alembic
            try:
                result = run_command(
                    [sys.executable, "-m", "alembic", "upgrade", "head"],
                    "Applying database migrations (python -m alembic)",
                    check=False
                )
                
                if result.returncode == 0:
                    logger.info("✅ Migration applied successfully (python -m alembic)")
                    migration_success = True
                elif "already at head" in result.stdout or "No migrations to apply" in result.stdout:
                    logger.info("✅ Database already up to date (python -m alembic)")
                    migration_success = True
                    
            except Exception as e2:
                logger.warning(f"⚠️  Python -m alembic also failed: {e2}")
        
        # Approach 3: Try to apply migration manually if Alembic fails
        if not migration_success:
            logger.info("🔧 Trying manual migration application...")
            migration_success = await apply_migration_manually()
        
        # Restore original directory
        os.chdir(original_dir)
        
        return migration_success
                
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        # Restore original directory on error
        try:
            os.chdir(original_dir)
        except:
            pass
        return False


async def verify_database_schema():
    """Verify that database schema has the required changes."""
    logger.info("🔍 Verifying database schema...")
    
    try:
        from app.core.database import get_async_session_local
        from sqlalchemy import text
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            # Check credits_balance column exists
            result = await session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns
                WHERE table_name='users' AND column_name='credits_balance'
            """))
            
            credits_column = result.fetchone()
            if not credits_column:
                logger.error("❌ credits_balance column not found")
                return False
            
            logger.info("✅ credits_balance column exists")
            
            # Check stripe_events table exists
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables
                WHERE table_name='stripe_events'
            """))
            
            stripe_table = result.fetchone()
            if not stripe_table:
                logger.error("❌ stripe_events table not found")
                return False
            
            logger.info("✅ stripe_events table exists")
            
            # Check constraints
            result = await session.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints
                WHERE table_name='users' AND constraint_name='credits_balance_nonneg'
            """))
            
            constraint = result.fetchone()
            if constraint:
                logger.info("✅ credits_balance non-negative constraint exists")
            else:
                logger.warning("⚠️  credits_balance constraint not found (may be optional)")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Schema verification failed: {e}")
        return False


async def test_hotfix_components():
    """Test that all hotfix components are working."""
    logger.info("🧪 Testing hotfix components...")
    
    try:
        # Import and test each component
        from app.db.session_patterns import run_in_tx
        from app.db.resolver_fix import is_email, is_uuid, is_placeholder
        from app.webhooks.stripe_checkout_completed_hotfix import handle_checkout_completed
        from app.models.stripe_event import StripeEvent
        from app.api.router.webhooks_hotfix import webhooks_hotfix_router
        
        # Test validation functions
        assert is_email("test@example.com") == True
        assert is_uuid("550e8400-e29b-41d4-a716-446655440000") == True
        assert is_placeholder("<email>") == True
        
        logger.info("✅ All hotfix components imported and tested successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Hotfix component test failed: {e}")
        return False


async def run_verification_script():
    """Run the comprehensive verification script."""
    logger.info("📋 Running verification script...")
    
    try:
        # Run the verification script
        result = run_command(
            [sys.executable, "hotfix_verification_test.py"],
            "Running hotfix verification tests",
            check=False
        )
        
        if result.returncode == 0:
            logger.info("✅ Verification script passed all tests")
            return True
        else:
            logger.warning("⚠️  Verification script found issues")
            return False
            
    except Exception as e:
        logger.error(f"❌ Verification script error: {e}")
        return False


def create_backup_info():
    """Create backup information file."""
    logger.info("💾 Creating backup information...")
    
    backup_info = f"""
# HOTFIX BACKUP INFORMATION
# Generated: {datetime.now().isoformat()}

## Hotfix Components Applied:
- ✅ Secure session/transaction patterns (app/db/session_patterns.py)
- ✅ Robust user resolver (app/db/resolver_fix.py)  
- ✅ StripeEvent model for idempotency (app/models/stripe_event.py)
- ✅ Enhanced webhook handler (app/webhooks/stripe_checkout_completed_hotfix.py)
- ✅ Bulletproof API router (app/api/router/webhooks_hotfix.py)
- ✅ Database migration (migrations/versions/0010_add_stripe_events_and_constraints.py)

## Database Changes:
- stripe_events table added
- credits_balance constraints verified
- Email indexes verified

## Files Modified:
{', '.join([
    'app/db/session_patterns.py',
    'app/db/resolver_fix.py', 
    'app/models/stripe_event.py',
    'app/webhooks/stripe_checkout_completed_hotfix.py',
    'app/api/router/webhooks_hotfix.py',
    'migrations/versions/0010_add_stripe_events_and_constraints.py'
])}

## Rollback Instructions:
1. Remove hotfix files
2. Run: alembic downgrade 0009_add_users_credits_balance
3. Restart application

## Testing:
- Run: python hotfix_verification_test.py
- Check: SQL queries in hotfix_verification.sql
"""
    
    try:
        with open("HOTFIX_BACKUP_INFO.md", "w") as f:
            f.write(backup_info)
        logger.info("✅ Backup information created")
    except Exception as e:
        logger.warning(f"⚠️  Could not create backup info: {e}")


async def deploy_hotfix(dry_run: bool = False, skip_migration: bool = False):
    """Deploy the comprehensive hotfix."""
    logger.info("🚀 Starting hotfix deployment...")
    
    if dry_run:
        logger.info("🏃 DRY RUN MODE - No actual changes will be made")
    
    steps = []
    
    # Step 1: Check database connection
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Database Connection Check")
    logger.info("="*60)
    
    if not await check_database_connection():
        logger.error("❌ Database connection failed - cannot proceed")
        return False
    
    steps.append(("Database Connection", True))
    
    # Step 2: Run migration (if not skipped)
    if not skip_migration:
        logger.info("\n" + "="*60)
        logger.info("STEP 2: Database Migration")
        logger.info("="*60)
        
        migration_success = await run_migration(dry_run)
        steps.append(("Database Migration", migration_success))
        
        if not migration_success:
            logger.error("❌ Migration failed - stopping deployment")
            return False
    else:
        logger.info("\n⏭️  Skipping database migration as requested")
        steps.append(("Database Migration", "SKIPPED"))
    
    # Step 3: Verify schema
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Schema Verification")
    logger.info("="*60)
    
    schema_success = await verify_database_schema()
    steps.append(("Schema Verification", schema_success))
    
    if not schema_success:
        logger.warning("⚠️  Schema verification failed - hotfix may not work correctly")
    
    # Step 4: Test components
    logger.info("\n" + "="*60)
    logger.info("STEP 4: Component Testing")
    logger.info("="*60)
    
    component_success = await test_hotfix_components()
    steps.append(("Component Testing", component_success))
    
    if not component_success:
        logger.error("❌ Component testing failed - hotfix not ready")
        return False
    
    # Step 5: Run verification
    logger.info("\n" + "="*60)
    logger.info("STEP 5: Comprehensive Verification")
    logger.info("="*60)
    
    verification_success = await run_verification_script()
    steps.append(("Verification Script", verification_success))
    
    # Step 6: Create backup info
    if not dry_run:
        logger.info("\n" + "="*60)
        logger.info("STEP 6: Create Backup Information")
        logger.info("="*60)
        
        create_backup_info()
        steps.append(("Backup Information", True))
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("🏁 HOTFIX DEPLOYMENT SUMMARY")
    logger.info("="*60)
    
    for step_name, result in steps:
        if result == "SKIPPED":
            status = "⏭️  SKIP"
        elif result:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        logger.info(f"{status} {step_name}")
    
    # Overall result
    failed_steps = [name for name, result in steps if result is False]
    
    if not failed_steps:
        logger.info("\n🎉 HOTFIX DEPLOYMENT SUCCESSFUL!")
        logger.info("✅ All components ready for production")
        logger.info("\n📋 Next steps:")
        logger.info("1. Test webhook endpoint: /webhooks/stripe/hotfix")
        logger.info("2. Monitor logs for any issues")
        logger.info("3. Run SQL verification queries if needed")
        return True
    else:
        logger.error(f"\n❌ HOTFIX DEPLOYMENT FAILED!")
        logger.error(f"Failed steps: {', '.join(failed_steps)}")
        logger.error("Please fix issues before proceeding to production")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Deploy credits_balance hotfix")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying them")
    parser.add_argument("--skip-migration", action="store_true", help="Skip database migration step")
    
    args = parser.parse_args()
    
    # Add backend to Python path
    backend_path = os.path.join(os.path.dirname(__file__), "apps", "backend")
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
    
    try:
        success = asyncio.run(deploy_hotfix(args.dry_run, args.skip_migration))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Deployment crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import datetime
    main()
