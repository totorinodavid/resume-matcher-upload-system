#!/usr/bin/env python3
"""
🚀 MIGRATION PREPARATION SCRIPT
Based on current Resume Matcher credit system analysis
Prepares for Next.js/Prisma migration with data validation
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationPreparation:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        
        self.engine = create_async_engine(self.database_url)
        self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        
        # Create migration directory
        self.migration_dir = Path("migration_data")
        self.migration_dir.mkdir(exist_ok=True)
        
        logger.info(f"Migration preparation initialized - Output directory: {self.migration_dir}")

    async def analyze_current_system(self):
        """Comprehensive analysis of current credit system"""
        logger.info("🔍 Analyzing current credit system...")
        
        async with self.async_session() as session:
            # Analyze users with credits
            users_query = text("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN credits_balance > 0 THEN 1 END) as users_with_credits,
                    SUM(COALESCE(credits_balance, 0)) as total_credits,
                    MIN(credits_balance) as min_credits,
                    MAX(credits_balance) as max_credits,
                    AVG(COALESCE(credits_balance, 0)) as avg_credits
                FROM users
            """)
            users_result = await session.execute(users_query)
            users_stats = dict(users_result.first()._mapping)
            
            # Analyze payments
            payments_query = text("""
                SELECT 
                    COUNT(*) as total_payments,
                    COUNT(CASE WHEN status = 'PAID' THEN 1 END) as paid_payments,
                    SUM(CASE WHEN status = 'PAID' THEN amount ELSE 0 END) as total_revenue,
                    COUNT(DISTINCT user_id) as unique_paying_users
                FROM payments
            """)
            payments_result = await session.execute(payments_query)
            payments_stats = dict(payments_result.first()._mapping)
            
            # Analyze credit transactions
            transactions_query = text("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(CASE WHEN delta > 0 THEN delta ELSE 0 END) as credits_added,
                    SUM(CASE WHEN delta < 0 THEN ABS(delta) ELSE 0 END) as credits_spent,
                    COUNT(DISTINCT user_id) as unique_transaction_users,
                    COUNT(DISTINCT reason) as unique_reasons
                FROM credit_transactions
            """)
            transactions_result = await session.execute(transactions_query)
            transactions_stats = dict(transactions_result.first()._mapping)
            
            # Check credit ledger (should be empty based on analysis)
            ledger_query = text("SELECT COUNT(*) as ledger_entries FROM credit_ledger")
            ledger_result = await session.execute(ledger_query)
            ledger_stats = dict(ledger_result.first()._mapping)
            
            analysis = {
                "analysis_timestamp": datetime.now().isoformat(),
                "database_url": self.database_url.split("@")[-1],  # Hide credentials
                "users": users_stats,
                "payments": payments_stats,
                "transactions": transactions_stats,
                "credit_ledger": ledger_stats,
                "system_health": {
                    "credit_balance_consistency": users_stats["total_credits"] > 0,
                    "payment_processing": payments_stats["paid_payments"] > 0,
                    "transaction_tracking": transactions_stats["total_transactions"] > 0,
                    "legacy_ledger_empty": ledger_stats["ledger_entries"] == 0
                }
            }
            
            # Save analysis
            with open(self.migration_dir / "current_system_analysis.json", "w") as f:
                json.dump(analysis, f, indent=2, default=str)
            
            logger.info(f"✅ System analysis completed:")
            logger.info(f"   - Users: {users_stats['total_users']} total, {users_stats['users_with_credits']} with credits")
            logger.info(f"   - Credits: {users_stats['total_credits']} total balance")
            logger.info(f"   - Payments: {payments_stats['paid_payments']} paid of {payments_stats['total_payments']} total")
            logger.info(f"   - Transactions: {transactions_stats['total_transactions']} total")
            
            return analysis

    async def export_migration_data(self):
        """Export all data needed for migration"""
        logger.info("📊 Exporting migration data...")
        
        async with self.async_session() as session:
            # Export users
            users_query = text("""
                SELECT 
                    id, email, credits_balance, stripe_customer_id,
                    created_at, updated_at
                FROM users 
                WHERE credits_balance > 0 OR stripe_customer_id IS NOT NULL
                ORDER BY created_at
            """)
            users_result = await session.execute(users_query)
            users_data = [dict(row._mapping) for row in users_result]
            
            # Export payments with user context
            payments_query = text("""
                SELECT 
                    p.id, p.user_id, p.stripe_payment_intent_id,
                    p.amount, p.status, p.created_at, p.updated_at,
                    u.email as user_email
                FROM payments p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at
            """)
            payments_result = await session.execute(payments_query)
            payments_data = [dict(row._mapping) for row in payments_result]
            
            # Export credit transactions with user context
            transactions_query = text("""
                SELECT 
                    ct.id, ct.user_id, ct.delta, ct.reason,
                    ct.stripe_event_id, ct.metadata, ct.created_at,
                    u.email as user_email
                FROM credit_transactions ct
                JOIN users u ON ct.user_id = u.id
                ORDER BY ct.created_at
            """)
            transactions_result = await session.execute(transactions_query)
            transactions_data = [dict(row._mapping) for row in transactions_result]
            
            # Save exports
            exports = {
                "users": users_data,
                "payments": payments_data,
                "transactions": transactions_data
            }
            
            for key, data in exports.items():
                with open(self.migration_dir / f"{key}_export.json", "w") as f:
                    json.dump(data, f, indent=2, default=str)
                logger.info(f"   - Exported {len(data)} {key}")
            
            return exports

    async def validate_data_integrity(self):
        """Validate data integrity before migration"""
        logger.info("🔍 Validating data integrity...")
        
        async with self.async_session() as session:
            # Check for orphaned records
            orphaned_payments = await session.execute(text("""
                SELECT COUNT(*) as count FROM payments p
                LEFT JOIN users u ON p.user_id = u.id
                WHERE u.id IS NULL
            """))
            
            orphaned_transactions = await session.execute(text("""
                SELECT COUNT(*) as count FROM credit_transactions ct
                LEFT JOIN users u ON ct.user_id = u.id
                WHERE u.id IS NULL
            """))
            
            # Check for duplicate stripe customer IDs
            duplicate_stripe = await session.execute(text("""
                SELECT stripe_customer_id, COUNT(*) as count
                FROM users
                WHERE stripe_customer_id IS NOT NULL
                GROUP BY stripe_customer_id
                HAVING COUNT(*) > 1
            """))
            
            # Check for negative credit balances
            negative_credits = await session.execute(text("""
                SELECT COUNT(*) as count FROM users
                WHERE credits_balance < 0
            """))
            
            integrity_issues = {
                "orphaned_payments": orphaned_payments.scalar(),
                "orphaned_transactions": orphaned_transactions.scalar(),
                "duplicate_stripe_customers": duplicate_stripe.rowcount,
                "negative_credit_balances": negative_credits.scalar()
            }
            
            # Save integrity report
            with open(self.migration_dir / "data_integrity_report.json", "w") as f:
                json.dump(integrity_issues, f, indent=2)
            
            total_issues = sum(integrity_issues.values())
            if total_issues == 0:
                logger.info("✅ Data integrity validation passed - no issues found")
            else:
                logger.warning(f"⚠️ Data integrity issues found: {integrity_issues}")
                
            return integrity_issues

    async def generate_migration_plan(self):
        """Generate detailed migration execution plan"""
        logger.info("📋 Generating migration plan...")
        
        # Load analysis data
        with open(self.migration_dir / "current_system_analysis.json", "r") as f:
            analysis = json.load(f)
        
        migration_plan = {
            "plan_version": "1.0",
            "created_at": datetime.now().isoformat(),
            "source_system": "Python/FastAPI/SQLAlchemy/PostgreSQL",
            "target_system": "Next.js/Prisma/PostgreSQL",
            "migration_phases": [
                {
                    "phase": 1,
                    "name": "Environment Setup",
                    "duration_estimate": "2-4 hours",
                    "tasks": [
                        "Create Next.js project with TypeScript",
                        "Setup Prisma with PostgreSQL",
                        "Configure Stripe integration",
                        "Setup Auth0 authentication",
                        "Create parallel database"
                    ],
                    "validation": "Environment runs locally with test data"
                },
                {
                    "phase": 2,
                    "name": "Data Migration",
                    "duration_estimate": "1-2 hours",
                    "tasks": [
                        f"Migrate {analysis['users']['total_users']} users",
                        f"Migrate {analysis['payments']['paid_payments']} payments",
                        f"Migrate {analysis['transactions']['total_transactions']} transactions",
                        f"Verify {analysis['users']['total_credits']} total credits"
                    ],
                    "validation": "Credit balances match exactly"
                },
                {
                    "phase": 3,
                    "name": "A/B Testing",
                    "duration_estimate": "1 week",
                    "tasks": [
                        "Deploy to staging environment",
                        "Start with 10% user rollout",
                        "Monitor metrics and error rates",
                        "Gradually increase to 50%"
                    ],
                    "validation": "Error rate < 1%, no credit loss"
                },
                {
                    "phase": 4,
                    "name": "Full Migration",
                    "duration_estimate": "1 week",
                    "tasks": [
                        "Complete user rollout",
                        "Deprecate legacy endpoints",
                        "Archive old system",
                        "Update documentation"
                    ],
                    "validation": "100% users on new system successfully"
                }
            ],
            "rollback_triggers": [
                "Credit loss detected",
                "Error rate > 5%",
                "Webhook failures > 10%",
                "User complaints increase"
            ],
            "success_metrics": {
                "zero_credit_loss": True,
                "error_rate_target": "< 1%",
                "response_time_target": "< 2s",
                "webhook_success_rate": "> 99.9%"
            }
        }
        
        with open(self.migration_dir / "migration_plan.json", "w") as f:
            json.dump(migration_plan, f, indent=2)
        
        logger.info("✅ Migration plan generated")
        return migration_plan

    async def create_backup(self):
        """Create complete backup of current system"""
        logger.info("💾 Creating system backup...")
        
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.migration_dir / f"backup_{backup_timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        async with self.async_session() as session:
            # Full database dump queries
            tables = ['users', 'payments', 'credit_transactions', 'credit_ledger']
            
            for table in tables:
                query = text(f"SELECT * FROM {table}")
                result = await session.execute(query)
                data = [dict(row._mapping) for row in result]
                
                with open(backup_dir / f"{table}_backup.json", "w") as f:
                    json.dump(data, f, indent=2, default=str)
                
                logger.info(f"   - Backed up {len(data)} records from {table}")
        
        # Create backup manifest
        manifest = {
            "backup_timestamp": backup_timestamp,
            "database_url": self.database_url.split("@")[-1],
            "tables_backed_up": tables,
            "backup_directory": str(backup_dir)
        }
        
        with open(backup_dir / "backup_manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"✅ Complete backup created in {backup_dir}")
        return backup_dir

    async def run_preparation(self):
        """Run complete migration preparation"""
        logger.info("🚀 Starting migration preparation...")
        
        try:
            # Step 1: Analyze current system
            analysis = await self.analyze_current_system()
            
            # Step 2: Validate data integrity
            integrity = await self.validate_data_integrity()
            
            # Step 3: Export migration data
            exports = await self.export_migration_data()
            
            # Step 4: Create backup
            backup_dir = await self.create_backup()
            
            # Step 5: Generate migration plan
            plan = await self.generate_migration_plan()
            
            # Final summary
            summary = {
                "preparation_completed": datetime.now().isoformat(),
                "system_analysis": analysis,
                "data_integrity": integrity,
                "exports_created": {k: len(v) for k, v in exports.items()},
                "backup_location": str(backup_dir),
                "migration_plan": "migration_plan.json",
                "ready_for_migration": sum(integrity.values()) == 0,
                "next_steps": [
                    "Review migration plan",
                    "Setup Next.js environment",
                    "Run data migration scripts",
                    "Start A/B testing"
                ]
            }
            
            with open(self.migration_dir / "preparation_summary.json", "w") as f:
                json.dump(summary, f, indent=2, default=str)
            
            logger.info("🎉 Migration preparation completed successfully!")
            logger.info(f"📊 Summary:")
            logger.info(f"   - {analysis['users']['total_users']} users analyzed")
            logger.info(f"   - {analysis['users']['total_credits']} credits to migrate")
            logger.info(f"   - Data integrity: {'✅ PASS' if summary['ready_for_migration'] else '❌ ISSUES'}")
            logger.info(f"   - All files saved to: {self.migration_dir}")
            
            if not summary['ready_for_migration']:
                logger.warning("⚠️ Data integrity issues found - review before proceeding!")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Migration preparation failed: {e}")
            raise
        finally:
            await self.engine.dispose()

async def main():
    """Main execution function"""
    try:
        preparation = MigrationPreparation()
        await preparation.run_preparation()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
