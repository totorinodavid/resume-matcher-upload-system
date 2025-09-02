#!/usr/bin/env python3
"""
🚀 FINAL MIGRATION PREPARATION
Works with actual                 # Export transactions
                logger.info("🔄 Exporting transactions...")
                transactions_export_query = text("""
                    SELECT 
                        id, user_id, delta_credits, reason,
                        payment_id, admin_action_id, meta, created_at
                    FROM credit_transactions 
                    ORDER BY created_at
                """)tcher database schema
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

class FinalMigrationPrep:
    def __init__(self):
        # Create migration directory
        self.migration_dir = Path("migration_data")
        self.migration_dir.mkdir(exist_ok=True)
        logger.info(f"Migration prep initialized - Output: {self.migration_dir}")

    async def analyze_and_export(self):
        """Analyze current system and export data"""
        logger.info("🔍 Final migration analysis for Next.js transition...")
        
        try:
            from app.core.database import get_async_session_local
        except ImportError:
            logger.error("Cannot import database session - check PYTHONPATH")
            return None
        
        session_factory = get_async_session_local()
        async with session_factory() as session:
            try:
                # Get basic stats
                logger.info("📊 Getting system statistics...")
                
                # Users stats
                users_stats_query = text("SELECT COUNT(*) as total_users, SUM(COALESCE(credits_balance, 0)) as total_credits FROM users")
                users_result = await session.execute(users_stats_query)
                users_stats = dict(users_result.first()._mapping)
                
                # Payments stats
                payments_stats_query = text("SELECT COUNT(*) as total_payments, COUNT(CASE WHEN status = 'PAID' THEN 1 END) as paid_payments FROM payments")
                payments_result = await session.execute(payments_stats_query)
                payments_stats = dict(payments_result.first()._mapping)
                
                # Transactions stats
                transactions_stats_query = text("SELECT COUNT(*) as total_transactions FROM credit_transactions")
                transactions_result = await session.execute(transactions_stats_query)
                transactions_stats = dict(transactions_result.first()._mapping)
                
                # Export all users with credits
                logger.info("👥 Exporting users...")
                users_export_query = text("SELECT id, email, name, credits_balance FROM users WHERE credits_balance > 0")
                users_export_result = await session.execute(users_export_query)
                users_data = [dict(row._mapping) for row in users_export_result]
                
                # Export all payments
                logger.info("💳 Exporting payments...")
                payments_export_query = text("""
                    SELECT 
                        id, user_id, provider_payment_intent_id, 
                        amount_total_cents, expected_credits, status, created_at
                    FROM payments 
                    ORDER BY created_at
                """)
                payments_export_result = await session.execute(payments_export_query)
                payments_data = [dict(row._mapping) for row in payments_export_result]
                
                # Export all transactions
                logger.info("🔄 Exporting transactions...")
                transactions_export_query = text("""
                    SELECT 
                        id, user_id, delta_credits, reason, 
                        stripe_event_id, metadata, created_at
                    FROM credit_transactions 
                    ORDER BY created_at
                """)
                transactions_export_result = await session.execute(transactions_export_query)
                transactions_data = [dict(row._mapping) for row in transactions_export_result]
                
                # Add user emails to payment and transaction data
                for payment in payments_data:
                    user_query = text("SELECT email FROM users WHERE id = :user_id")
                    user_result = await session.execute(user_query, {"user_id": int(payment["user_id"])})
                    user_row = user_result.first()
                    payment["user_email"] = user_row.email if user_row else "unknown"
                
                for transaction in transactions_data:
                    user_query = text("SELECT email FROM users WHERE id = :user_id")
                    user_result = await session.execute(user_query, {"user_id": int(transaction["user_id"])})
                    user_row = user_result.first()
                    transaction["user_email"] = user_row.email if user_row else "unknown"
                
                # Create comprehensive analysis
                analysis = {
                    "migration_timestamp": datetime.now().isoformat(),
                    "source_system": {
                        "platform": "Resume Matcher",
                        "backend": "Python/FastAPI/SQLAlchemy",
                        "database": "PostgreSQL (Neon)",
                        "credit_model": "users.credits_balance + credit_transactions audit"
                    },
                    "target_system": {
                        "platform": "Resume Matcher Next.js",
                        "backend": "Next.js 14 App Router + Prisma",
                        "database": "PostgreSQL (Prisma)",
                        "credit_model": "users.credits + credit_transactions unified"
                    },
                    "migration_data": {
                        "users_total": users_stats["total_users"],
                        "users_with_credits": len(users_data),
                        "total_credits": users_stats["total_credits"],
                        "payments_total": payments_stats["total_payments"], 
                        "payments_paid": payments_stats["paid_payments"],
                        "transactions_total": transactions_stats["total_transactions"]
                    },
                    "database_schema": {
                        "users_table": "id(int), email(varchar), name(varchar), credits_balance(int)",
                        "payments_table": "id(bigint), user_id(text), provider_payment_intent_id(varchar), amount_total_cents(int), expected_credits(int), status(enum), created_at(timestamptz)",
                        "credit_transactions_table": "id(bigint), user_id(text), payment_id(bigint), admin_action_id(bigint), delta_credits(int), reason(text), meta(json), created_at(timestamptz)"
                    },
                    "migration_strategy": {
                        "phase_1": "Setup Next.js + Prisma environment",
                        "phase_2": "Migrate user data with credit balances",
                        "phase_3": "Migrate payment history as credit transactions",
                        "phase_4": "Migrate existing credit transactions",
                        "phase_5": "Validate total credits match",
                        "phase_6": "A/B test and gradual rollout"
                    }
                }
                
                # Save analysis
                with open(self.migration_dir / "final_migration_analysis.json", "w") as f:
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
                
                # Generate Prisma schema for Next.js
                prisma_schema = self.generate_prisma_schema()
                with open(self.migration_dir / "schema.prisma", "w") as f:
                    f.write(prisma_schema)
                
                # Generate Next.js migration script
                migration_script = self.generate_nextjs_migration(analysis, exports)
                with open(self.migration_dir / "nextjs_migration.ts", "w") as f:
                    f.write(migration_script)
                
                # Generate setup instructions
                setup_instructions = self.generate_setup_instructions(analysis)
                with open(self.migration_dir / "MIGRATION_SETUP.md", "w") as f:
                    f.write(setup_instructions)
                
                # Create final summary
                summary = {
                    "preparation_completed": datetime.now().isoformat(),
                    "migration_ready": True,
                    "files_created": [
                        "final_migration_analysis.json",
                        "users_export.json",
                        "payments_export.json", 
                        "transactions_export.json",
                        "schema.prisma",
                        "nextjs_migration.ts",
                        "MIGRATION_SETUP.md",
                        "migration_summary.json"
                    ],
                    "key_metrics": {
                        "users_to_migrate": len(users_data),
                        "credits_to_preserve": users_stats["total_credits"],
                        "payments_to_import": len(payments_data),
                        "transactions_to_import": len(transactions_data)
                    },
                    "critical_validations": {
                        "credit_balance_preservation": f"Must maintain exactly {users_stats['total_credits']} credits",
                        "payment_history_integrity": f"Must preserve {payments_stats['paid_payments']} paid transactions",
                        "audit_trail_completeness": f"Must migrate {transactions_stats['total_transactions']} transaction records"
                    },
                    "next_steps": [
                        "1. Review final_migration_analysis.json",
                        "2. Follow MIGRATION_SETUP.md instructions", 
                        "3. Setup Next.js project with schema.prisma",
                        "4. Run nextjs_migration.ts script",
                        "5. Validate credit totals match exactly",
                        "6. Begin A/B testing with 10% rollout"
                    ]
                }
                
                with open(self.migration_dir / "migration_summary.json", "w") as f:
                    json.dump(summary, f, indent=2, default=str)
                
                logger.info("✅ Migration preparation completed!")
                logger.info(f"📊 Results:")
                logger.info(f"   - Users: {users_stats['total_users']} total, {len(users_data)} with credits")
                logger.info(f"   - Credits: {users_stats['total_credits']} total balance to preserve")
                logger.info(f"   - Payments: {payments_stats['paid_payments']} paid of {payments_stats['total_payments']} total")
                logger.info(f"   - Transactions: {transactions_stats['total_transactions']} audit records")
                logger.info(f"   - Files: {len(summary['files_created'])} migration files created")
                logger.info(f"   - Location: {self.migration_dir}")
                
                return summary
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                raise

    def generate_prisma_schema(self):
        """Generate Prisma schema for Next.js"""
        return '''// Resume Matcher Next.js Migration - Prisma Schema
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id               String             @id @default(cuid())
  email            String             @unique
  name             String?
  credits          Int                @default(0)
  
  // Migration tracking
  legacyUserId     String?            @unique  // Original user ID from Python system
  migratedAt       DateTime?          // When migration occurred
  
  // Stripe integration
  stripeCustomerId String?            @unique
  
  // Timestamps
  createdAt        DateTime           @default(now())
  updatedAt        DateTime           @updatedAt
  
  // Relations
  transactions     CreditTransaction[]
  resumes          Resume[]
  
  @@map("users")
}

model CreditTransaction {
  id            String   @id @default(cuid())
  userId        String
  delta         Int      // positive for purchases, negative for spending
  reason        String   // "purchase", "spend", "refund", "migration"
  stripeEventId String?  @unique // for Stripe idempotency
  
  // Migration tracking
  legacyTransactionId String? @unique
  migratedFrom        String? // "legacy_payment" | "legacy_transaction"
  
  // Flexible metadata
  metadata      Json?    
  
  createdAt     DateTime @default(now())
  
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("credit_transactions")
}

model Resume {
  id          String   @id @default(cuid())
  userId      String
  filename    String
  content     Json     // Structured resume data
  creditsUsed Int      @default(1) // Credits spent for processing
  createdAt   DateTime @default(now())
  
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("resumes")
}

model Price {
  id             String  @id @default(cuid())
  stripePriceId  String  @unique
  creditsPerUnit Int
  priceInCents   Int
  currency       String  @default("eur")
  active         Boolean @default(true)
  createdAt      DateTime @default(now())

  @@map("prices")
}'''

    def generate_nextjs_migration(self, analysis, exports):
        """Generate TypeScript migration script"""
        return f'''// Resume Matcher Migration Script: Python → Next.js
// Generated: {datetime.now().isoformat()}
// Total Credits to Preserve: {analysis["migration_data"]["total_credits"]}

import {{ PrismaClient }} from '@prisma/client'

const prisma = new PrismaClient()

interface LegacyUser {{
  id: number
  email: string
  name: string | null
  credits_balance: number
}}

interface LegacyPayment {{
  id: string
  user_id: string
  provider_payment_intent_id: string | null
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
  payment_id: number | null
  admin_action_id: number | null
  meta: any
  created_at: string
  user_email: string
}}

async function validatePreMigration() {{
  console.log('🔍 Pre-migration validation...')
  
  // Check if any data already exists
  const existingUsers = await prisma.user.count()
  const existingTransactions = await prisma.creditTransaction.count()
  
  if (existingUsers > 0 || existingTransactions > 0) {{
    console.log(`⚠️  Database not empty: ${{existingUsers}} users, ${{existingTransactions}} transactions`)
    console.log('Run with --force to override, or reset database first')
    return false
  }}
  
  return true
}}

async function migrateUsers() {{
  console.log('👥 Migrating {len(exports["users"])} users with credits...')
  
  const legacyUsers: LegacyUser[] = require('./users_export.json')
  let migratedCount = 0
  
  for (const user of legacyUsers) {{
    const newUser = await prisma.user.create({{
      data: {{
        email: user.email,
        name: user.name,
        credits: user.credits_balance,
        legacyUserId: user.id.toString(),
        migratedAt: new Date(),
      }}
    }})
    
    migratedCount++
    console.log(`   ✅ ${{user.email}}: ${{user.credits_balance}} credits`)
  }}
  
  console.log(`✅ Migrated ${{migratedCount}} users`)
  return migratedCount
}}

async function migratePaymentHistory() {{
  console.log('💳 Migrating {len(exports["payments"])} payment records as transactions...')
  
  const legacyPayments: LegacyPayment[] = require('./payments_export.json')
  let migratedCount = 0
  
  for (const payment of legacyPayments) {{
    if (payment.status === 'PAID') {{
      // Find migrated user
      const user = await prisma.user.findUnique({{
        where: {{ email: payment.user_email }}
      }})
      
      if (user) {{
        await prisma.creditTransaction.create({{
          data: {{
            userId: user.id,
            delta: payment.expected_credits,
            reason: 'migration_payment',
            legacyTransactionId: payment.id,
            migratedFrom: 'legacy_payment',
            metadata: {{
              originalAmount: payment.amount_total_cents,
              stripePaymentIntentId: payment.provider_payment_intent_id,
              migratedAt: new Date().toISOString(),
            }},
            createdAt: new Date(payment.created_at),
          }}
        }})
        
        migratedCount++
      }}
    }}
  }}
  
  console.log(`✅ Migrated ${{migratedCount}} payment records`)
  return migratedCount
}}

async function migrateCreditTransactions() {{
  console.log('🔄 Migrating {len(exports["transactions"])} existing credit transactions...')
  
  const legacyTransactions: LegacyTransaction[] = require('./transactions_export.json')
  let migratedCount = 0
  
  for (const transaction of legacyTransactions) {{
    // Find migrated user
    const user = await prisma.user.findUnique({{
      where: {{ email: transaction.user_email }}
    }})
    
    if (user) {{
      await prisma.creditTransaction.create({{
        data: {{
          userId: user.id,
          delta: transaction.delta_credits,
          reason: transaction.reason || 'legacy',
          legacyTransactionId: transaction.id,
          migratedFrom: 'legacy_transaction',
          metadata: transaction.meta || {{}},
          createdAt: new Date(transaction.created_at),
        }}
      }})
      
      migratedCount++
    }}
  }}
  
  console.log(`✅ Migrated ${{migratedCount}} credit transactions`)
  return migratedCount
}}

async function validatePostMigration() {{
  console.log('🔍 Post-migration validation...')
  
  // Check total credits
  const totalCredits = await prisma.user.aggregate({{
    _sum: {{ credits: true }}
  }})
  
  const expectedCredits = {analysis["migration_data"]["total_credits"]}
  
  if (totalCredits._sum.credits === expectedCredits) {{
    console.log(`✅ Credit validation passed: ${{totalCredits._sum.credits}} credits preserved`)
  }} else {{
    console.log(`❌ Credit validation FAILED: Expected ${{expectedCredits}}, got ${{totalCredits._sum.credits}}`)
    return false
  }}
  
  // Check user count
  const userCount = await prisma.user.count({{ where: {{ migratedAt: {{ not: null }} }} }})
  console.log(`✅ Migrated ${{userCount}} users`)
  
  // Check transaction count
  const transactionCount = await prisma.creditTransaction.count()
  console.log(`✅ Created ${{transactionCount}} transaction records`)
  
  return true
}}

async function main() {{
  console.log('🚀 Resume Matcher Migration: Python/SQLAlchemy → Next.js/Prisma')
  console.log('=' .repeat(60))
  
  try {{
    // Validation
    const isValid = await validatePreMigration()
    if (!isValid && !process.argv.includes('--force')) {{
      process.exit(1)
    }}
    
    // Migration steps
    const userCount = await migrateUsers()
    const paymentCount = await migratePaymentHistory()
    const transactionCount = await migrateCreditTransactions()
    
    // Final validation
    const validationPassed = await validatePostMigration()
    
    if (validationPassed) {{
      console.log('\\n🎉 Migration completed successfully!')
      console.log('📊 Summary:')
      console.log(`   - Users migrated: ${{userCount}}`)
      console.log(`   - Payment history: ${{paymentCount}} records`)
      console.log(`   - Credit transactions: ${{transactionCount}} records`)
      console.log(`   - Total credits preserved: {analysis["migration_data"]["total_credits"]}`)
      console.log('\\nNext steps:')
      console.log('1. Test credit operations in development')
      console.log('2. Setup Stripe webhook endpoints')
      console.log('3. Begin A/B testing with 10% rollout')
    }} else {{
      console.log('\\n💥 Migration validation failed!')
      process.exit(1)
    }}
    
  }} catch (error) {{
    console.error('Migration failed:', error)
    process.exit(1)
  }} finally {{
    await prisma.$disconnect()
  }}
}}

// Run migration
main().catch(console.error)

// Usage:
// npm install && npx prisma generate
// npx ts-node nextjs_migration.ts
// 
// To force migration on non-empty database:
// npx ts-node nextjs_migration.ts --force
'''

    def generate_setup_instructions(self, analysis):
        """Generate setup instructions markdown"""
        return f'''# 🚀 Resume Matcher Migration: Python → Next.js

## Overview

This migration transitions the Resume Matcher credit system from:
- **Source**: Python/FastAPI/SQLAlchemy → PostgreSQL
- **Target**: Next.js 14/Prisma → PostgreSQL

## Migration Data Summary

- **Users**: {analysis["migration_data"]["users_total"]} total, {analysis["migration_data"]["users_with_credits"]} with credits
- **Credits**: {analysis["migration_data"]["total_credits"]} total credits to preserve
- **Payments**: {analysis["migration_data"]["payments_paid"]} successful payments
- **Transactions**: {analysis["migration_data"]["transactions_total"]} audit records

## 📋 Step-by-Step Migration

### 1. Environment Setup

```bash
# Create new Next.js project
npx create-next-app@latest resume-matcher-nextjs --typescript --tailwind --app

cd resume-matcher-nextjs

# Install dependencies
npm install @prisma/client prisma stripe @auth0/nextjs-auth0
npm install -D @types/node tsx

# Initialize Prisma
npx prisma init
```

### 2. Database Configuration

```bash
# Copy the generated schema.prisma to prisma/schema.prisma
cp ../migration_data/schema.prisma prisma/schema.prisma

# Set up environment variables
echo "DATABASE_URL=\\"postgresql://user:pass@host:5432/database\\"" > .env
echo "STRIPE_SECRET_KEY=sk_test_..." >> .env
echo "STRIPE_WEBHOOK_SECRET=whsec_..." >> .env
```

### 3. Database Migration

```bash
# Generate Prisma client
npx prisma generate

# Create and run migration
npx prisma migrate dev --name initial_migration

# Verify empty database
npx prisma studio
```

### 4. Data Migration

```bash
# Copy migration files
cp ../migration_data/*.json .
cp ../migration_data/nextjs_migration.ts .

# Install TypeScript runner
npm install -D tsx

# Run migration
npx tsx nextjs_migration.ts
```

### 5. Validation

```bash
# Open Prisma Studio to verify data
npx prisma studio

# Check totals:
# - Users table: {analysis["migration_data"]["users_with_credits"]} users
# - Credit total: {analysis["migration_data"]["total_credits"]} credits
# - Transactions: payment + transaction records
```

### 6. Stripe Integration

```bash
# Install Stripe CLI
# Follow: https://stripe.com/docs/stripe-cli

# Set up webhook forwarding
stripe listen --forward-to localhost:3000/api/stripe/webhook

# Test webhook processing
stripe trigger checkout.session.completed
```

### 7. Testing Strategy

#### A/B Testing Setup
```typescript
// lib/feature-flags.ts
export function shouldUseNewSystem(userEmail: string): boolean {{
  // Start with 10% rollout
  const hash = userEmail.split('').reduce((a, b) => {{
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }}, 0)
  
  return Math.abs(hash) % 100 < 10
}}
```

#### Validation Metrics
- Credit balance accuracy: 100% match
- Transaction completeness: All records preserved
- Webhook reliability: >99% success rate
- Performance: <2s response time

### 8. Rollout Plan

1. **Week 1**: 10% A/B test
2. **Week 2**: 25% rollout
3. **Week 3**: 50% rollout
4. **Week 4**: 100% migration

### 9. Rollback Strategy

If issues occur:
```bash
# Emergency rollback
export NEXT_PUBLIC_LEGACY_FALLBACK=true

# Restore from backup if needed
psql database < backup.sql
```

## 🔍 Critical Validations

### Pre-Migration Checklist
- [ ] Backup current database
- [ ] Export migration data verified
- [ ] Next.js environment tested
- [ ] Stripe integration configured

### Post-Migration Checklist
- [ ] Credit totals match exactly: {analysis["migration_data"]["total_credits"]}
- [ ] All users migrated: {analysis["migration_data"]["users_with_credits"]}
- [ ] Payment history preserved: {analysis["migration_data"]["payments_paid"]}
- [ ] Transaction audit complete: {analysis["migration_data"]["transactions_total"]}
- [ ] Webhook processing functional
- [ ] Error rates <1%

## 🚨 Emergency Contacts

- Database issues: Check connection strings and permissions
- Credit discrepancies: Compare totals before/after migration  
- Stripe problems: Verify webhook endpoints and secrets
- Performance issues: Monitor query performance and indexing

## 📊 Success Metrics

- **Zero credit loss** during migration
- **100% data integrity** for payment history
- **<2 second response times** for credit operations
- **>99.9% webhook success rate**
- **User satisfaction maintained**

Migration prepared: {analysis["migration_timestamp"]}
Ready for execution! 🚀
'''

async def run_prep():
    """Run final migration preparation"""
    prep = FinalMigrationPrep()
    await prep.analyze_and_export()

if __name__ == "__main__":
    asyncio.run(run_prep())
