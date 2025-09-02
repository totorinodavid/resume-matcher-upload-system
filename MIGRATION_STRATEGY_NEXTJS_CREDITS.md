# 🚀 Migration Strategy: Python/SQLAlchemy → Next.js/Prisma Credit System

## 📊 Current System Analysis (aus Chatverlauf)

### Aktuelle Architektur:
- **Backend**: Python 3.13, FastAPI, SQLAlchemy (async), PostgreSQL (Neon/Render)
- **Credit System**: Dual-Table Approach mit Inkonsistenzen
  - `users.credits_balance` (200 credits) ← Aktuelle Balances
  - `credit_ledger` (leer) ← Legacy/unused
  - `credit_transactions` (1 Transaktion) ← Audit Trail
  - `payments` (1 PAID entry) ← Stripe Payments

### Identifizierte Probleme:
1. **Architectural Inconsistency**: CreditsService nutzt `credit_ledger` statt `users.credits_balance`
2. **Production Failures**: Transaction rollback cascades bei Webhook-Verarbeitung
3. **Emergency Hotfixes**: UltraEmergencyUserService für Production-Stabilität
4. **Balance Discrepancy**: UI zeigt 0 credits, DB hat 200 credits

---

## 🎯 Migration Ziele

### Primäre Ziele:
- ✅ **Konsistente Credit-Architektur** mit einheitlicher Balance-Berechnung
- ✅ **Robuste Webhook-Verarbeitung** ohne Transaction-Cascades
- ✅ **Moderne Tech Stack** (Next.js 14, Prisma, TypeScript)
- ✅ **Simplified Database Schema** mit klarer Credit-Logik
- ✅ **Production-Ready** von Tag 1

### Sekundäre Ziele:
- 🔄 **Seamless Data Migration** ohne Credit-Verlust
- 📊 **Improved Analytics** mit besserem Transaction-Tracking
- 🛡️ **Enhanced Security** mit moderner Authentication
- ⚡ **Better Performance** mit optimierten Queries

---

## 📋 Pre-Migration Audit

### 1. Current Data Assessment
```bash
# Führe aktuelle System-Analyse durch
python analyze_credit_system.py

# Expected Output:
# - Users: 1 with 200 credits in credits_balance
# - Payments: 1 PAID transaction
# - Credit Transactions: 1 entry
# - Credit Ledger: empty (architectural issue)
```

### 2. Backup Critical Data
```sql
-- Export current credits data
COPY (
  SELECT 
    id, email, credits_balance, created_at, updated_at,
    stripe_customer_id
  FROM users 
  WHERE credits_balance > 0
) TO '/tmp/users_backup.csv' WITH CSV HEADER;

-- Export payment history
COPY (
  SELECT 
    id, user_id, stripe_payment_intent_id, amount, status,
    created_at, updated_at
  FROM payments
) TO '/tmp/payments_backup.csv' WITH CSV HEADER;

-- Export transaction history
COPY (
  SELECT 
    id, user_id, delta, reason, stripe_event_id, metadata,
    created_at
  FROM credit_transactions
) TO '/tmp/transactions_backup.csv' WITH CSV HEADER;
```

---

## 🔄 Migration Phases

### Phase 1: Next.js System Setup (Parallel Deployment)
```bash
# 1. Create new Next.js project
npx create-next-app@latest resume-matcher-nextjs --typescript --tailwind --app

# 2. Setup dependencies
cd resume-matcher-nextjs
npm install stripe @prisma/client @auth0/nextjs-auth0
npm install -D prisma

# 3. Initialize Prisma with PostgreSQL (matching current)
npx prisma init --datasource-provider postgresql
```

### Phase 2: Data Schema Migration
```prisma
// prisma/schema.prisma - Enhanced für Resume Matcher
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
  auth0Id          String?            @unique  // Auth0 integration
  stripeCustomerId String?            @unique
  credits          Int                @default(0)
  
  // Migration fields
  legacyUserId     String?            @unique  // Map to old system
  migratedAt       DateTime?
  
  createdAt        DateTime           @default(now())
  updatedAt        DateTime           @updatedAt
  
  // Relations
  transactions     CreditTransaction[]
  resumes          Resume[]
  jobAnalyses      JobAnalysis[]

  @@map("users")
}

model CreditTransaction {
  id            String   @id @default(cuid())
  userId        String
  delta         Int      // positive for purchases, negative for spending
  reason        String   // "purchase", "spend", "refund", "migration"
  stripeEventId String?  @unique // for idempotency
  metadata      Json?    // flexible additional data
  
  // Migration tracking
  legacyTransactionId String? @unique
  migratedFrom        String? // "legacy_payment" | "legacy_transaction"
  
  createdAt     DateTime @default(now())
  
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("credit_transactions")
}

model Resume {
  id          String   @id @default(cuid())
  userId      String
  filename    String
  content     Json     // Structured resume data
  creditsUsed Int      @default(0)
  createdAt   DateTime @default(now())
  
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("resumes")
}

model JobAnalysis {
  id          String   @id @default(cuid())
  userId      String
  resumeId    String?
  jobContent  Json     // Job description data
  matchScore  Float?   // 0-100 match percentage
  creditsUsed Int      @default(10) // Cost per analysis
  createdAt   DateTime @default(now())
  
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  
  @@map("job_analyses")
}

model Price {
  id             String  @id @default(cuid())
  stripePriceId  String  @unique
  creditsPerUnit Int
  priceInCents   Int     // Store price for display
  currency       String  @default("eur")
  active         Boolean @default(true)
  createdAt      DateTime @default(now())

  @@map("prices")
}
```

### Phase 3: Data Migration Script
```typescript
// scripts/migrate-data.ts
import { PrismaClient } from '@prisma/client'
import { Client } from 'pg'

const prisma = new PrismaClient()
const legacyDb = new Client({
  connectionString: process.env.LEGACY_DATABASE_URL
})

async function migrateUsers() {
  console.log('🔄 Migrating users...')
  
  const legacyUsers = await legacyDb.query(`
    SELECT id, email, credits_balance, stripe_customer_id, created_at, updated_at
    FROM users 
    WHERE credits_balance > 0 OR stripe_customer_id IS NOT NULL
  `)

  for (const user of legacyUsers.rows) {
    await prisma.user.upsert({
      where: { email: user.email },
      update: {
        credits: user.credits_balance || 0,
        stripeCustomerId: user.stripe_customer_id,
        migratedAt: new Date(),
      },
      create: {
        email: user.email,
        legacyUserId: user.id,
        credits: user.credits_balance || 0,
        stripeCustomerId: user.stripe_customer_id,
        migratedAt: new Date(),
        createdAt: user.created_at,
      }
    })
  }
  
  console.log(`✅ Migrated ${legacyUsers.rows.length} users`)
}

async function migrateTransactions() {
  console.log('🔄 Migrating credit transactions...')
  
  // Migrate payments as credit transactions
  const legacyPayments = await legacyDb.query(`
    SELECT p.*, u.email 
    FROM payments p
    JOIN users u ON p.user_id = u.id
    WHERE p.status = 'PAID'
  `)

  for (const payment of legacyPayments.rows) {
    const user = await prisma.user.findUnique({
      where: { email: payment.email }
    })
    
    if (user) {
      // Estimate credits from payment amount (assuming €0.05 per credit)
      const estimatedCredits = Math.floor((payment.amount || 500) / 5)
      
      await prisma.creditTransaction.create({
        data: {
          userId: user.id,
          delta: estimatedCredits,
          reason: 'migration',
          legacyTransactionId: payment.id,
          migratedFrom: 'legacy_payment',
          metadata: {
            originalAmount: payment.amount,
            stripePaymentIntentId: payment.stripe_payment_intent_id,
            migratedAt: new Date().toISOString(),
          },
          createdAt: payment.created_at,
        }
      })
    }
  }

  // Migrate existing credit transactions
  const legacyTransactions = await legacyDb.query(`
    SELECT ct.*, u.email 
    FROM credit_transactions ct
    JOIN users u ON ct.user_id = u.id
  `)

  for (const transaction of legacyTransactions.rows) {
    const user = await prisma.user.findUnique({
      where: { email: transaction.email }
    })
    
    if (user) {
      await prisma.creditTransaction.create({
        data: {
          userId: user.id,
          delta: transaction.delta,
          reason: transaction.reason || 'legacy',
          stripeEventId: transaction.stripe_event_id,
          legacyTransactionId: transaction.id,
          migratedFrom: 'legacy_transaction',
          metadata: transaction.metadata || {},
          createdAt: transaction.created_at,
        }
      })
    }
  }
  
  console.log(`✅ Migrated transactions`)
}

async function validateMigration() {
  console.log('🔍 Validating migration...')
  
  const newTotalCredits = await prisma.user.aggregate({
    _sum: { credits: true }
  })
  
  const legacyTotalCredits = await legacyDb.query(`
    SELECT SUM(credits_balance) as total FROM users
  `)
  
  console.log(`Legacy total credits: ${legacyTotalCredits.rows[0].total}`)
  console.log(`New total credits: ${newTotalCredits._sum.credits}`)
  
  if (newTotalCredits._sum.credits === parseInt(legacyTotalCredits.rows[0].total)) {
    console.log('✅ Credit migration validated successfully!')
  } else {
    console.log('❌ Credit migration validation failed!')
    process.exit(1)
  }
}

async function main() {
  await legacyDb.connect()
  
  try {
    await migrateUsers()
    await migrateTransactions()
    await validateMigration()
  } finally {
    await legacyDb.end()
    await prisma.$disconnect()
  }
}

main().catch(console.error)
```

### Phase 4: Parallel Testing Environment
```bash
# Environment setup for parallel testing
# .env.local (Next.js)
DATABASE_URL="postgresql://user:pass@localhost:5432/resume_matcher_nextjs"
LEGACY_DATABASE_URL="postgresql://user:pass@neon.tech/resume_matcher_legacy"
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_BASE_URL="http://localhost:3001"
AUTH0_SECRET="..."
AUTH0_BASE_URL="http://localhost:3001"
AUTH0_ISSUER_BASE_URL="https://your-tenant.auth0.com"
AUTH0_CLIENT_ID="..."
AUTH0_CLIENT_SECRET="..."
```

### Phase 5: A/B Testing Setup
```typescript
// lib/feature-flags.ts
export const FEATURES = {
  NEW_CREDIT_SYSTEM: process.env.NEXT_PUBLIC_NEW_CREDIT_SYSTEM === 'true',
  LEGACY_FALLBACK: process.env.NEXT_PUBLIC_LEGACY_FALLBACK === 'true',
} as const

// Gradual rollout strategy
export function shouldUseNewSystem(userEmail: string): boolean {
  if (FEATURES.LEGACY_FALLBACK) return false
  
  // Rollout to 10% of users initially
  const hash = userEmail.split('').reduce((a, b) => {
    a = ((a << 5) - a) + b.charCodeAt(0)
    return a & a
  }, 0)
  
  return Math.abs(hash) % 100 < 10
}
```

---

## 🚀 Deployment Strategy

### Rollout Plan:
1. **Week 1**: Setup parallel Next.js system, data migration
2. **Week 2**: A/B test with 10% of users
3. **Week 3**: Increase to 50% if metrics are positive
4. **Week 4**: Full migration, legacy system deprecation

### Rollback Strategy:
```typescript
// Emergency rollback procedure
if (errorRate > 5% || creditLoss > 0) {
  // Automatic fallback to legacy system
  process.env.NEXT_PUBLIC_LEGACY_FALLBACK = 'true'
  
  // Alert monitoring
  console.error('EMERGENCY: Rolling back to legacy credit system')
}
```

### Monitoring & Metrics:
- Credit balance consistency
- Transaction processing latency
- Webhook success rates
- User experience metrics
- Error rates and types

---

## ✅ Migration Checklist

### Pre-Migration:
- [ ] Backup all credit-related data
- [ ] Setup Next.js parallel environment
- [ ] Test Stripe integration in new system
- [ ] Validate data migration scripts
- [ ] Setup monitoring and alerting

### During Migration:
- [ ] Run data migration with validation
- [ ] Deploy Next.js system to staging
- [ ] A/B test with small user group
- [ ] Monitor metrics and error rates
- [ ] Gradual rollout based on success metrics

### Post-Migration:
- [ ] Validate all credits migrated correctly
- [ ] Monitor webhook processing stability
- [ ] Deprecate legacy credit endpoints
- [ ] Update documentation
- [ ] Archive legacy credit system

---

## 🔍 Risk Mitigation

### High Risk: Credit Loss
- **Mitigation**: Comprehensive backup before migration
- **Fallback**: Keep legacy system running in parallel
- **Validation**: Automated credit balance verification

### Medium Risk: Webhook Failures
- **Mitigation**: Robust error handling and retries
- **Fallback**: Manual credit adjustment procedures
- **Monitoring**: Real-time webhook success rate tracking

### Low Risk: Performance Issues
- **Mitigation**: Database indexing and query optimization
- **Fallback**: Horizontal scaling options
- **Monitoring**: Response time and throughput metrics

---

## 📊 Success Metrics

### Technical Metrics:
- Zero credit loss during migration
- <2s response time for credit operations
- 99.9% webhook processing success rate
- <1% error rate in new system

### Business Metrics:
- Maintained user satisfaction scores
- No increase in support tickets
- Improved conversion rates
- Better analytics insights

---

Diese Migration-Strategie berücksichtigt alle Erkenntnisse aus unserem Chatverlauf und bereitet eine sichere, schrittweise Migration vor! 🚀
