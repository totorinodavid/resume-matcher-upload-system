"""
PRODUCTION-READY DATABASE VIEW MIGRATION
Creates missing v_credit_balance view with proper error handling and logging
"""

import asyncio
import asyncpg
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def create_production_view():
    """
    Production-ready function to create v_credit_balance view
    """
    # Production database URL
    database_url = "postgresql://resume_user:KNv2zOO0g2bZIqyB8zEeo4pYRlbBBBHY@dpg-d2qkqqqdbo4c73c8ngeg-a.oregon-postgres.render.com/resume_matcher_db_e3f7"
    
    try:
        logger.info("🚀 Starting production database view creation")
        
        # Connect with async pool for production
        conn = await asyncpg.connect(database_url, ssl='require')
        
        logger.info("✅ Database connection established")
        
        # Check if view already exists
        view_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views 
                WHERE table_name = 'v_credit_balance'
            )
        """)
        
        if view_exists:
            logger.info("⚠️  View v_credit_balance already exists - recreating")
        
        # Create/replace the view with production-grade SQL
        create_view_sql = """
        CREATE OR REPLACE VIEW v_credit_balance AS
        SELECT 
            user_id,
            COALESCE(SUM(delta), 0)::INTEGER AS balance,
            COUNT(*) AS transaction_count,
            MAX(created_at) AS last_transaction
        FROM credit_ledger
        WHERE user_id IS NOT NULL
        GROUP BY user_id
        HAVING COALESCE(SUM(delta), 0) >= 0;
        """
        
        logger.info("📝 Creating production v_credit_balance view...")
        await conn.execute(create_view_sql)
        
        # Verify creation and get stats
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(*) as user_count,
                SUM(balance) as total_credits,
                AVG(balance) as avg_balance,
                MAX(balance) as max_balance
            FROM v_credit_balance
        """)
        
        # Test view with sample data
        sample_users = await conn.fetch("""
            SELECT user_id, balance, transaction_count, last_transaction
            FROM v_credit_balance 
            ORDER BY balance DESC 
            LIMIT 5
        """)
        
        logger.info("✅ View v_credit_balance created successfully")
        logger.info(f"📊 Stats: {stats['user_count']} users, {stats['total_credits']} total credits")
        logger.info(f"📊 Avg balance: {stats['avg_balance']:.2f}, Max: {stats['max_balance']}")
        
        # Log sample data
        for user in sample_users:
            logger.info(f"   User: {user['user_id'][:8]}..., Balance: {user['balance']}, Transactions: {user['transaction_count']}")
        
        # Create indexes for performance
        try:
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_credit_ledger_user_id_created 
                ON credit_ledger(user_id, created_at DESC)
            """)
            logger.info("✅ Performance index created")
        except Exception as e:
            logger.warning(f"⚠️  Index creation skipped: {e}")
        
        await conn.close()
        
        logger.info("🎉 PRODUCTION VIEW CREATION COMPLETE")
        return True
        
    except Exception as e:
        logger.error(f"❌ Production view creation failed: {e}")
        return False

async def validate_credits_system():
    """
    Validate that the credits system is working properly
    """
    database_url = "postgresql://resume_user:KNv2zOO0g2bZIqyB8zEeo4pYRlbBBBHY@dpg-d2qkqqqdbo4c73c8ngeg-a.oregon-postgres.render.com/resume_matcher_db_e3f7"
    
    try:
        conn = await asyncpg.connect(database_url, ssl='require')
        
        # Test all credit-related queries
        tests = [
            ("View exists", "SELECT 1 FROM v_credit_balance LIMIT 1"),
            ("User balance query", "SELECT balance FROM v_credit_balance WHERE user_id = (SELECT user_id FROM v_credit_balance LIMIT 1)"),
            ("Ledger query", "SELECT SUM(delta) FROM credit_ledger WHERE user_id IS NOT NULL"),
            ("Tables exist", "SELECT 1 FROM credit_ledger, stripe_sessions, users LIMIT 1")
        ]
        
        logger.info("🧪 Running production validation tests...")
        
        for test_name, query in tests:
            try:
                result = await conn.fetchval(query)
                logger.info(f"✅ {test_name}: PASS")
            except Exception as e:
                logger.error(f"❌ {test_name}: FAIL - {e}")
                return False
        
        await conn.close()
        logger.info("🎯 ALL PRODUCTION TESTS PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        return False

async def main():
    """
    Main production deployment function
    """
    logger.info("=" * 60)
    logger.info("🚀 PRODUCTION CREDITS SYSTEM DEPLOYMENT")
    logger.info("=" * 60)
    
    # Step 1: Create view
    view_success = await create_production_view()
    if not view_success:
        logger.error("❌ PRODUCTION DEPLOYMENT FAILED")
        return False
    
    # Step 2: Validate system
    validation_success = await validate_credits_system()
    if not validation_success:
        logger.error("❌ PRODUCTION VALIDATION FAILED")
        return False
    
    logger.info("=" * 60)
    logger.info("🎉 PRODUCTION DEPLOYMENT SUCCESSFUL")
    logger.info("✅ Credits system is production-ready")
    logger.info("✅ All validations passed")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
