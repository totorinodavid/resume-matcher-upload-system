import { PrismaClient } from '@prisma/client'
import * as fs from 'fs'
import * as path from 'path'

const prisma = new PrismaClient()

// Load exported data from migration_data directory
function loadMigrationData() {
  const dataDir = path.join(__dirname, 'migration_data')
  
  const usersData = JSON.parse(fs.readFileSync(path.join(dataDir, 'users_export.json'), 'utf8'))
  const paymentsData = JSON.parse(fs.readFileSync(path.join(dataDir, 'payments_export.json'), 'utf8'))
  const transactionsData = JSON.parse(fs.readFileSync(path.join(dataDir, 'transactions_export.json'), 'utf8'))
  const summaryData = JSON.parse(fs.readFileSync(path.join(dataDir, 'export_summary.json'), 'utf8'))
  
  return { usersData, paymentsData, transactionsData, summaryData }
}

async function migrateFromResumeMatcherPython() {
  console.log('🚀 Starting Resume Matcher Migration: Python → Next.js')
  console.log('=' * 60)
  
  try {
    // Load actual exported data
    const { usersData, paymentsData, transactionsData, summaryData } = loadMigrationData()
    
    console.log(`📊 Migration Data Loaded:`)
    console.log(`- Users: ${summaryData.users_exported}`)
    console.log(`- Payments: ${summaryData.payments_exported}`)
    console.log(`- Transactions: ${summaryData.transactions_exported}`)
    console.log(`- Total Credits: ${summaryData.total_credits}`)
    console.log('')
    
    // Clear existing data (for testing)
    console.log('🧹 Clearing existing Next.js data...')
    await prisma.creditTransaction.deleteMany()
    await prisma.user.deleteMany()
    
    let totalCreditsAdded = 0
    
    // Migrate each user
    for (const legacyUser of usersData) {
      console.log(`👤 Migrating user: ${legacyUser.email} (${legacyUser.credits_balance} credits)`)
      
      // Create user in Next.js system
      const user = await prisma.user.create({
        data: {
          email: legacyUser.email,
          name: legacyUser.name,
          credits: legacyUser.credits_balance,
          legacyUserId: legacyUser.id.toString(),
          migratedAt: new Date(),
        }
      })
      
      totalCreditsAdded += legacyUser.credits_balance
      
      // Migrate payments as credit transactions
      const userPayments = paymentsData.filter(p => p.user_id === legacyUser.id.toString())
      
      for (const payment of userPayments) {
        console.log(`💳 Migrating payment: €${payment.amount_total_cents/100} → ${payment.expected_credits} credits`)
        
        await prisma.creditTransaction.create({
          data: {
            userId: user.id,
            delta: payment.expected_credits,
            reason: 'migration_payment',
            legacyTransactionId: payment.id.toString(),
            migratedFrom: 'legacy_payment',
            metadata: {
              originalAmount: payment.amount_total_cents,
              currency: 'eur',
              stripePaymentIntentId: payment.provider_payment_intent_id,
              status: payment.status,
              migratedAt: new Date().toISOString(),
              sourceSystem: 'resume_matcher_python'
            },
            createdAt: new Date(), // Use current time since no created_at in legacy
          }
        })
      }
      
      // Migrate credit transactions
      const userTransactions = transactionsData.filter(t => t.user_id === legacyUser.id.toString())
      
      for (const transaction of userTransactions) {
        console.log(`📝 Migrating transaction: ${transaction.delta_credits > 0 ? '+' : ''}${transaction.delta_credits} credits`)
        
        await prisma.creditTransaction.create({
          data: {
            userId: user.id,
            delta: transaction.delta_credits,
            reason: transaction.reason || 'migration_transaction',
            legacyTransactionId: transaction.id.toString(),
            migratedFrom: 'legacy_transaction',
            metadata: {
              originalReason: transaction.reason,
              paymentId: transaction.payment_id,
              adminActionId: transaction.admin_action_id,
              originalMeta: transaction.meta,
              migratedAt: new Date().toISOString(),
              sourceSystem: 'resume_matcher_python'
            },
            createdAt: new Date(transaction.created_at),
          }
        })
      }
      
      // If user has more credits than payments, create adjustment transaction
      const totalPaymentCredits = userPayments.reduce((sum, p) => sum + p.expected_credits, 0)
      const totalTransactionCredits = userTransactions.reduce((sum, t) => sum + Math.max(0, t.delta_credits), 0)
      const creditDifference = legacyUser.credits_balance - totalPaymentCredits - totalTransactionCredits
      
      if (creditDifference > 0) {
        console.log(`🔄 Adding adjustment: +${creditDifference} credits (balance correction)`)
        
        await prisma.creditTransaction.create({
          data: {
            userId: user.id,
            delta: creditDifference,
            reason: 'migration_adjustment',
            metadata: {
              note: `Balance adjustment to match legacy credits: ${legacyUser.credits_balance}`,
              legacyBalance: legacyUser.credits_balance,
              accountedCredits: totalPaymentCredits + totalTransactionCredits,
              migratedAt: new Date().toISOString(),
              sourceSystem: 'resume_matcher_python'
            }
          }
        })
      }
      
      console.log(`✅ User ${legacyUser.email} migrated successfully`)
      console.log('')
    }
    
    // Validation
    console.log('🔍 Validating migration...')
    
    const migratedUsers = await prisma.user.findMany({
      include: {
        transactions: true
      }
    })
    
    const totalNewCredits = await prisma.user.aggregate({
      _sum: { credits: true }
    })
    
    const totalTransactionDelta = await prisma.creditTransaction.aggregate({
      _sum: { delta: true }
    })
    
    console.log(`📈 Migration Results:`)
    console.log(`- Users migrated: ${migratedUsers.length}`)
    console.log(`- Total credits in system: ${totalNewCredits._sum.credits}`)
    console.log(`- Total transaction deltas: ${totalTransactionDelta._sum.delta}`)
    console.log(`- Expected credits (legacy): ${summaryData.total_credits}`)
    console.log('')
    
    // Verify credit balance matches
    if (totalNewCredits._sum.credits !== summaryData.total_credits) {
      throw new Error(
        `❌ CREDIT MISMATCH! Expected ${summaryData.total_credits}, got ${totalNewCredits._sum.credits}`
      )
    }
    
    console.log('🎉 MIGRATION SUCCESSFUL!')
    console.log(`✅ All ${summaryData.total_credits} credits preserved`)
    console.log(`✅ ${migratedUsers.length} users migrated`)
    console.log(`✅ Data integrity verified`)
    
    // Migration summary
    for (const user of migratedUsers) {
      console.log(`👤 ${user.email}: ${user.credits} credits (${user.transactions.length} transactions)`)
    }
    
  } catch (error) {
    console.error('❌ Migration failed:', error)
    throw error
  } finally {
    await prisma.$disconnect()
  }
}

// Execute migration
if (require.main === module) {
  migrateFromResumeMatcherPython()
    .then(() => {
      console.log('\n🚀 Ready for Next.js Resume Matcher!')
      process.exit(0)
    })
    .catch((error) => {
      console.error('\n💥 Migration failed:', error)
      process.exit(1)
    })
}

export { migrateFromResumeMatcherPython }
