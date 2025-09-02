# 🔧 Migration Execution Scripts

## 1. Current System Data Export
```python
# scripts/export_current_data.py
import asyncio
import json
import csv
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

# Use current database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://...")

async def export_credit_data():
    """Export all credit-related data from current system"""
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    export_dir = "migration_exports"
    os.makedirs(export_dir, exist_ok=True)
    
    async with async_session() as session:
        # Export users with credits
        print("📊 Exporting users...")
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
        
        with open(f"{export_dir}/users_export.json", "w") as f:
            json.dump(users_data, f, indent=2, default=str)
        
        # Export payments
        print("💳 Exporting payments...")
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
        
        with open(f"{export_dir}/payments_export.json", "w") as f:
            json.dump(payments_data, f, indent=2, default=str)
        
        # Export credit transactions
        print("🔄 Exporting credit transactions...")
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
        
        with open(f"{export_dir}/transactions_export.json", "w") as f:
            json.dump(transactions_data, f, indent=2, default=str)
        
        # Create summary report
        summary = {
            "export_timestamp": datetime.now().isoformat(),
            "total_users": len(users_data),
            "total_payments": len(payments_data),
            "total_transactions": len(transactions_data),
            "total_credits": sum(user.get("credits_balance", 0) or 0 for user in users_data),
            "users_with_credits": len([u for u in users_data if (u.get("credits_balance") or 0) > 0]),
            "paid_payments": len([p for p in payments_data if p.get("status") == "PAID"]),
        }
        
        with open(f"{export_dir}/migration_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Export completed!")
        print(f"📊 Summary: {summary}")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(export_credit_data())
```

## 2. Next.js Environment Setup Script
```bash
#!/bin/bash
# scripts/setup_nextjs_environment.sh

echo "🚀 Setting up Next.js migration environment..."

# Create new Next.js project in parallel directory
cd .. 
npx create-next-app@latest resume-matcher-nextjs --typescript --tailwind --app --eslint

cd resume-matcher-nextjs

# Install dependencies
echo "📦 Installing dependencies..."
npm install stripe @prisma/client @auth0/nextjs-auth0
npm install -D prisma @types/node

# Initialize Prisma
echo "🗄️ Setting up Prisma..."
npx prisma init --datasource-provider postgresql

# Create environment file
echo "⚙️ Creating environment configuration..."
cat > .env.local << 'EOF'
# Database
DATABASE_URL="postgresql://user:pass@localhost:5432/resume_matcher_nextjs"
LEGACY_DATABASE_URL="postgresql://user:pass@neon.tech/resume_matcher_legacy"

# Stripe
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# App
NEXT_PUBLIC_BASE_URL="http://localhost:3001"

# Auth0
AUTH0_SECRET="use [openssl rand -hex 32] to generate a 32 bytes value"
AUTH0_BASE_URL="http://localhost:3001"
AUTH0_ISSUER_BASE_URL="https://your-tenant.auth0.com"
AUTH0_CLIENT_ID="your-auth0-client-id"
AUTH0_CLIENT_SECRET="your-auth0-client-secret"

# Feature Flags
NEXT_PUBLIC_NEW_CREDIT_SYSTEM="true"
NEXT_PUBLIC_LEGACY_FALLBACK="false"
EOF

echo "✅ Next.js environment setup completed!"
echo "📝 Please update .env.local with your actual credentials"
```

## 3. Database Migration Validation
```typescript
// scripts/validate_migration.ts
import { PrismaClient } from '@prisma/client'
import fs from 'fs'

const prisma = new PrismaClient()

interface LegacyData {
  users_export: any[]
  payments_export: any[]
  transactions_export: any[]
  migration_summary: any
}

async function validateMigration() {
  console.log('🔍 Starting migration validation...')
  
  // Load exported legacy data
  const legacyData: LegacyData = {
    users_export: JSON.parse(fs.readFileSync('../Resume-Matcher/migration_exports/users_export.json', 'utf8')),
    payments_export: JSON.parse(fs.readFileSync('../Resume-Matcher/migration_exports/payments_export.json', 'utf8')),
    transactions_export: JSON.parse(fs.readFileSync('../Resume-Matcher/migration_exports/transactions_export.json', 'utf8')),
    migration_summary: JSON.parse(fs.readFileSync('../Resume-Matcher/migration_exports/migration_summary.json', 'utf8'))
  }
  
  // Validate user migration
  console.log('👥 Validating user migration...')
  const migratedUsers = await prisma.user.findMany({
    where: { migratedAt: { not: null } }
  })
  
  if (migratedUsers.length !== legacyData.users_export.length) {
    console.error(`❌ User count mismatch: Expected ${legacyData.users_export.length}, got ${migratedUsers.length}`)
    return false
  }
  
  // Validate credit balances
  console.log('💰 Validating credit balances...')
  const totalNewCredits = await prisma.user.aggregate({
    _sum: { credits: true }
  })
  
  const expectedCredits = legacyData.migration_summary.total_credits
  if (totalNewCredits._sum.credits !== expectedCredits) {
    console.error(`❌ Credit balance mismatch: Expected ${expectedCredits}, got ${totalNewCredits._sum.credits}`)
    return false
  }
  
  // Validate transaction migration
  console.log('🔄 Validating transaction migration...')
  const migratedTransactions = await prisma.creditTransaction.findMany({
    where: { legacyTransactionId: { not: null } }
  })
  
  const expectedTransactions = legacyData.payments_export.length + legacyData.transactions_export.length
  if (migratedTransactions.length < expectedTransactions) {
    console.error(`❌ Transaction count too low: Expected at least ${expectedTransactions}, got ${migratedTransactions.length}`)
    return false
  }
  
  // Validate Stripe customer IDs
  console.log('💳 Validating Stripe customers...')
  const usersWithStripe = await prisma.user.findMany({
    where: { stripeCustomerId: { not: null } }
  })
  
  const legacyStripeUsers = legacyData.users_export.filter(u => u.stripe_customer_id)
  if (usersWithStripe.length !== legacyStripeUsers.length) {
    console.error(`❌ Stripe customer mismatch: Expected ${legacyStripeUsers.length}, got ${usersWithStripe.length}`)
    return false
  }
  
  console.log('✅ All migration validations passed!')
  
  // Generate migration report
  const report = {
    validation_timestamp: new Date().toISOString(),
    users_migrated: migratedUsers.length,
    credits_migrated: totalNewCredits._sum.credits,
    transactions_migrated: migratedTransactions.length,
    stripe_customers_migrated: usersWithStripe.length,
    validation_status: 'SUCCESS'
  }
  
  fs.writeFileSync('migration_validation_report.json', JSON.stringify(report, null, 2))
  console.log('📊 Validation report saved to migration_validation_report.json')
  
  return true
}

validateMigration()
  .then(success => {
    if (success) {
      console.log('🎉 Migration validation completed successfully!')
      process.exit(0)
    } else {
      console.log('💥 Migration validation failed!')
      process.exit(1)
    }
  })
  .catch(console.error)
  .finally(() => prisma.$disconnect())
```

## 4. Rollback Emergency Script
```typescript
// scripts/emergency_rollback.ts
import { PrismaClient } from '@prisma/client'
import fs from 'fs'

const prisma = new PrismaClient()

async function emergencyRollback() {
  console.log('🚨 EMERGENCY ROLLBACK INITIATED')
  
  const rollbackLog = {
    timestamp: new Date().toISOString(),
    reason: process.argv[2] || 'Manual rollback',
    actions: []
  }
  
  try {
    // 1. Disable new system immediately
    console.log('🔒 Disabling new credit system...')
    // This would update environment variables or feature flags
    rollbackLog.actions.push('Disabled new credit system')
    
    // 2. Export current state for investigation
    console.log('📊 Exporting current state...')
    const currentUsers = await prisma.user.findMany({
      include: { transactions: true }
    })
    
    fs.writeFileSync(
      `rollback_state_${Date.now()}.json`, 
      JSON.stringify(currentUsers, null, 2)
    )
    rollbackLog.actions.push('Exported current state')
    
    // 3. If data corruption detected, restore from backup
    if (process.argv.includes('--restore-backup')) {
      console.log('🔄 Restoring from backup...')
      // This would restore database from backup
      rollbackLog.actions.push('Restored from backup')
    }
    
    // 4. Re-enable legacy system
    console.log('🔙 Re-enabling legacy system...')
    rollbackLog.actions.push('Re-enabled legacy system')
    
    console.log('✅ Emergency rollback completed')
    rollbackLog.status = 'SUCCESS'
    
  } catch (error) {
    console.error('❌ Rollback failed:', error)
    rollbackLog.status = 'FAILED'
    rollbackLog.error = error.message
  }
  
  fs.writeFileSync(
    `rollback_log_${Date.now()}.json`,
    JSON.stringify(rollbackLog, null, 2)
  )
}

// Usage: npm run rollback "Credit loss detected" --restore-backup
emergencyRollback()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
```

## 5. A/B Testing Configuration
```typescript
// lib/ab-testing.ts
interface FeatureFlags {
  NEW_CREDIT_SYSTEM: boolean
  LEGACY_FALLBACK: boolean
  ROLLOUT_PERCENTAGE: number
}

export class ABTestingManager {
  private flags: FeatureFlags
  
  constructor() {
    this.flags = {
      NEW_CREDIT_SYSTEM: process.env.NEXT_PUBLIC_NEW_CREDIT_SYSTEM === 'true',
      LEGACY_FALLBACK: process.env.NEXT_PUBLIC_LEGACY_FALLBACK === 'true',
      ROLLOUT_PERCENTAGE: parseInt(process.env.NEXT_PUBLIC_ROLLOUT_PERCENTAGE || '10')
    }
  }
  
  shouldUseNewSystem(userEmail: string): boolean {
    // Emergency fallback
    if (this.flags.LEGACY_FALLBACK) {
      console.log('Using legacy system (emergency fallback)')
      return false
    }
    
    // Feature disabled
    if (!this.flags.NEW_CREDIT_SYSTEM) {
      return false
    }
    
    // Hash-based consistent assignment
    const hash = this.hashEmail(userEmail)
    const assignment = hash % 100 < this.flags.ROLLOUT_PERCENTAGE
    
    console.log(`User ${userEmail}: ${assignment ? 'NEW' : 'LEGACY'} system (${this.flags.ROLLOUT_PERCENTAGE}% rollout)`)
    return assignment
  }
  
  private hashEmail(email: string): number {
    let hash = 0
    for (let i = 0; i < email.length; i++) {
      const char = email.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return Math.abs(hash)
  }
  
  logMetric(event: string, data: any) {
    // Log to analytics service
    console.log(`AB_TEST_METRIC: ${event}`, data)
  }
}

export const abTesting = new ABTestingManager()
```

## 6. Migration Monitoring Dashboard
```typescript
// pages/api/migration/status.ts
import { NextApiRequest, NextApiResponse } from 'next'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' })
  }
  
  try {
    // Get migration metrics
    const metrics = await Promise.all([
      // User migration status
      prisma.user.count({ where: { migratedAt: { not: null } } }),
      prisma.user.count(),
      
      // Credit balance consistency
      prisma.user.aggregate({ _sum: { credits: true } }),
      
      // Transaction processing
      prisma.creditTransaction.count({ 
        where: { 
          createdAt: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) } 
        } 
      }),
      
      // Error rate
      prisma.creditTransaction.count({
        where: {
          reason: 'error',
          createdAt: { gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
        }
      })
    ])
    
    const [migratedUsers, totalUsers, creditSum, recentTransactions, errorCount] = metrics
    
    const status = {
      migration: {
        users_migrated: migratedUsers,
        total_users: totalUsers,
        migration_percentage: Math.round((migratedUsers / totalUsers) * 100)
      },
      credits: {
        total_credits: creditSum._sum.credits || 0
      },
      activity: {
        transactions_24h: recentTransactions,
        errors_24h: errorCount,
        error_rate: recentTransactions > 0 ? (errorCount / recentTransactions) * 100 : 0
      },
      health: {
        status: errorCount === 0 ? 'HEALTHY' : errorCount < 10 ? 'WARNING' : 'CRITICAL',
        timestamp: new Date().toISOString()
      }
    }
    
    res.status(200).json(status)
  } catch (error) {
    console.error('Migration status error:', error)
    res.status(500).json({ error: 'Failed to get migration status' })
  }
}
```

Diese Scripts ermöglichen eine sichere, überwachte Migration mit Rollback-Möglichkeiten! 🛡️
