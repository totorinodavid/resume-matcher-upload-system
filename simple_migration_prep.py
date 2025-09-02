#!/usr/bin/env python3
"""
🚀 SIMPLIFIED MIGRATION PREPARATION
Compatible with existing Resume Matcher environment
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
import logging

# Add current directory to path for imports
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'apps', 'backend'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleMigrationPrep:
    def __init__(self):
        # Create migration directory
        self.migration_dir = Path("migration_data")
        self.migration_dir.mkdir(exist_ok=True)
        logger.info(f"Migration prep initialized - Output: {self.migration_dir}")

    async def analyze_and_export(self):
        """Analyze current system and export data"""
        logger.info("🔍 Analyzing current system for Next.js migration...")
        
        try:
            from app.core.database import get_async_session_local
        except ImportError:
            logger.error("Cannot import database session - check PYTHONPATH")
            return None
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            try:
                # Get user stats
                users_query = text("""
                    SELECT 
                        COUNT(*) as total_users,
                        COUNT(CASE WHEN credits_balance > 0 THEN 1 END) as users_with_credits,
                        SUM(COALESCE(credits_balance, 0)) as total_credits,
                        MAX(credits_balance) as max_credits
                    FROM users
                """)
                users_result = await session.execute(users_query)
                users_stats = dict(users_result.first()._mapping)
                
                # Get payment stats
                payments_query = text("""
                    SELECT 
                        COUNT(*) as total_payments,
                        COUNT(CASE WHEN status = 'PAID' THEN 1 END) as paid_payments,
                        SUM(CASE WHEN status = 'PAID' THEN COALESCE(amount_total_cents, 0) ELSE 0 END) as total_revenue
                    FROM payments
                """)
                payments_result = await session.execute(payments_query)
                payments_stats = dict(payments_result.first()._mapping)
                
                # Get transaction stats
                transactions_query = text("""
                    SELECT 
                        COUNT(*) as total_transactions,
                        SUM(CASE WHEN delta_credits > 0 THEN delta_credits ELSE 0 END) as credits_added,
                        SUM(CASE WHEN delta_credits < 0 THEN ABS(delta_credits) ELSE 0 END) as credits_spent
                    FROM credit_transactions
                """)
                transactions_result = await session.execute(transactions_query)
                transactions_stats = dict(transactions_result.first()._mapping)
                
                # Export users with credits
                users_export_query = text("""
                    SELECT 
                        id, email, name, credits_balance
                    FROM users 
                    WHERE credits_balance > 0 OR id IN (
                        SELECT DISTINCT user_id FROM payments WHERE status = 'PAID'
                    )
                    ORDER BY id
                """)
                users_export_result = await session.execute(users_export_query)
                users_data = [dict(row._mapping) for row in users_export_result]
                
                # Export payments
                payments_export_query = text("""
                    SELECT 
                        p.id, p.user_id, p.provider_payment_intent_id as stripe_payment_intent_id,
                        p.amount_total_cents, p.expected_credits, p.status,
                        p.created_at, u.email as user_email
                    FROM payments p
                    JOIN users u ON p.user_id::integer = u.id
                    ORDER BY p.created_at
                """)
                payments_export_result = await session.execute(payments_export_query)
                payments_data = [dict(row._mapping) for row in payments_export_result]
                
                # Export transactions
                transactions_export_query = text("""
                    SELECT 
                        ct.id, ct.user_id, ct.delta_credits, ct.reason,
                        ct.stripe_event_id, ct.metadata, ct.created_at,
                        u.email as user_email
                    FROM credit_transactions ct
                    JOIN users u ON ct.user_id::integer = u.id
                    ORDER BY ct.created_at
                """)
                transactions_export_result = await session.execute(transactions_export_query)
                transactions_data = [dict(row._mapping) for row in transactions_export_result]
                
                # Create comprehensive analysis
                analysis = {
                    "migration_prep_timestamp": datetime.now().isoformat(),
                    "current_system": {
                        "backend": "Python/FastAPI/SQLAlchemy",
                        "database": "PostgreSQL (Neon)",
                        "credit_architecture": "Dual table (users.credits_balance + credit_transactions)"
                    },
                    "target_system": {
                        "backend": "Next.js 14 App Router",
                        "database": "PostgreSQL (Prisma)",
                        "credit_architecture": "Unified (users.credits + credit_transactions)"
                    },
                    "statistics": {
                        "users": users_stats,
                        "payments": payments_stats,
                        "transactions": transactions_stats
                    },
                    "migration_data": {
                        "users_to_migrate": len(users_data),
                        "payments_to_migrate": len(payments_data),
                        "transactions_to_migrate": len(transactions_data)
                    },
                    "data_integrity": {
                        "credits_balance_positive": users_stats["total_credits"] > 0,
                        "payments_exist": payments_stats["paid_payments"] > 0,
                        "transactions_tracked": transactions_stats["total_transactions"] > 0
                    }
                }
                
                # Save analysis
                with open(self.migration_dir / "migration_analysis.json", "w") as f:
                    json.dump(analysis, f, indent=2, default=str)
                
                # Save export data
                exports = {
                    "users": users_data,
                    "payments": payments_data,
                    "transactions": transactions_data
                }
                
                for key, data in exports.items():
                    with open(self.migration_dir / f"{key}_export.json", "w") as f:
                        json.dump(data, f, indent=2, default=str)
                    logger.info(f"   - Exported {len(data)} {key}")
                
                # Generate Next.js migration script
                migration_script = self.generate_nextjs_migration_script(analysis, exports)
                with open(self.migration_dir / "nextjs_migration_script.ts", "w") as f:
                    f.write(migration_script)
                
                # Generate summary
                summary = {
                    "preparation_completed": datetime.now().isoformat(),
                    "files_created": [
                        "migration_analysis.json",
                        "users_export.json", 
                        "payments_export.json",
                        "transactions_export.json",
                        "nextjs_migration_script.ts",
                        "migration_summary.json"
                    ],
                    "next_steps": [
                        "1. Review migration analysis",
                        "2. Setup Next.js project",
                        "3. Run nextjs_migration_script.ts",
                        "4. Validate migrated data",
                        "5. Start A/B testing"
                    ],
                    "key_metrics": {
                        "users_with_credits": users_stats["users_with_credits"],
                        "total_credits": users_stats["total_credits"],
                        "paid_payments": payments_stats["paid_payments"],
                        "total_transactions": transactions_stats["total_transactions"]
                    }
                }
                
                with open(self.migration_dir / "migration_summary.json", "w") as f:
                    json.dump(summary, f, indent=2, default=str)
                
                logger.info("✅ Migration preparation completed!")
                logger.info(f"📊 Summary:")
                logger.info(f"   - Users: {users_stats['total_users']} total, {users_stats['users_with_credits']} with credits")
                logger.info(f"   - Credits: {users_stats['total_credits']} total balance")
                logger.info(f"   - Payments: {payments_stats['paid_payments']} successful")
                logger.info(f"   - Transactions: {transactions_stats['total_transactions']} recorded")
                logger.info(f"   - Files saved to: {self.migration_dir}")
                
                return summary
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                raise

    def generate_nextjs_migration_script(self, analysis, exports):
        """Generate TypeScript migration script for Next.js"""
        return f'''// Next.js Migration Script
// Generated: {datetime.now().isoformat()}
// Source: Resume Matcher Python/SQLAlchemy system

import {{ PrismaClient }} from '@prisma/client'
import migrationData from './migration_analysis.json'

const prisma = new PrismaClient()

interface LegacyUser {{
  id: string
  email: string
  name: string
  credits_balance: number
  created_at: string
  updated_at: string
}}

interface LegacyPayment {{
  id: string
  user_id: string
  stripe_payment_intent_id: string | null
  amount_total_cents: number
  expected_credits: number
  status: string
  created_at: string
  user_email: string
}}

interface LegacyTransaction {{
  id: string
  user_id: string
  delta_credits: number
  reason: string
  stripe_event_id: string | null
  metadata: any
  created_at: string
  user_email: string
}}

async function migrateUsers() {{
  console.log('🔄 Migrating {len(exports["users"])} users...')
  
  const legacyUsers: LegacyUser[] = require('./users_export.json')
  
  for (const user of legacyUsers) {{
    await prisma.user.upsert({{
      where: {{ email: user.email }},
      update: {{
        credits: user.credits_balance || 0,
        migratedAt: new Date(),
      }},
      create: {{
        email: user.email,
        legacyUserId: user.id,
        credits: user.credits_balance || 0,
        migratedAt: new Date(),
        createdAt: new Date(user.created_at),
      }}
    }})
  }}
  
  console.log('✅ Users migrated')
}}

async function migrateTransactions() {{
  console.log('🔄 Migrating transactions...')
  
  const legacyPayments: LegacyPayment[] = require('./payments_export.json')
  const legacyTransactions: LegacyTransaction[] = require('./transactions_export.json')
  
  // Migrate payments as credit transactions
  for (const payment of legacyPayments) {{
    if (payment.status === 'PAID') {{
      const user = await prisma.user.findUnique({{
        where: {{ email: payment.user_email }}
      }})
      
      if (user) {{
        await prisma.creditTransaction.create({{
          data: {{
            userId: user.id,
            delta: payment.expected_credits || 0,
            reason: 'migration_payment',
            legacyTransactionId: payment.id,
            migratedFrom: 'legacy_payment',
            metadata: {{
              originalAmount: payment.amount_total_cents,
              stripePaymentIntentId: payment.stripe_payment_intent_id,
              migratedAt: new Date().toISOString(),
            }},
            createdAt: new Date(payment.created_at),
          }}
        }})
      }}
    }}
  }}
  
  // Migrate existing transactions
  for (const transaction of legacyTransactions) {{
    const user = await prisma.user.findUnique({{
      where: {{ email: transaction.user_email }}
    }})
    
    if (user) {{
      await prisma.creditTransaction.create({{
        data: {{
          userId: user.id,
          delta: transaction.delta_credits,
          reason: transaction.reason || 'legacy',
          stripeEventId: transaction.stripe_event_id,
          legacyTransactionId: transaction.id,
          migratedFrom: 'legacy_transaction',
          metadata: transaction.metadata || {{}},
          createdAt: new Date(transaction.created_at),
        }}
      }})
    }}
  }}
  
  console.log('✅ Transactions migrated')
}}

async function validateMigration() {{
  console.log('🔍 Validating migration...')
  
  const totalCredits = await prisma.user.aggregate({{
    _sum: {{ credits: true }}
  }})
  
  const expectedCredits = {analysis["statistics"]["users"]["total_credits"]}
  
  if (totalCredits._sum.credits === expectedCredits) {{
    console.log('✅ Credit migration validated successfully!')
    return true
  }} else {{
    console.log(`❌ Credit validation failed: Expected ${{expectedCredits}}, got ${{totalCredits._sum.credits}}`)
    return false
  }}
}}

async function main() {{
  console.log('🚀 Starting Resume Matcher migration to Next.js/Prisma...')
  
  try {{
    await migrateUsers()
    await migrateTransactions()
    
    const isValid = await validateMigration()
    
    if (isValid) {{
      console.log('🎉 Migration completed successfully!')
    }} else {{
      console.log('💥 Migration validation failed!')
      process.exit(1)
    }}
  }} catch (error) {{
    console.error('Migration failed:', error)
    process.exit(1)
  }} finally {{
    await prisma.$disconnect()
  }}
}}

main().catch(console.error)

// Usage:
// 1. Setup Next.js project with Prisma
// 2. Copy migration files to project
// 3. Run: npm install && npx prisma generate
// 4. Run: npx ts-node nextjs_migration_script.ts
'''

async def run_prep():
    """Run migration preparation"""
    prep = SimpleMigrationPrep()
    await prep.analyze_and_export()

if __name__ == "__main__":
    asyncio.run(run_prep())
