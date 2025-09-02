import { PrismaClient } from '@prisma/client'

declare global {
  // eslint-disable-next-line no-var
  var __prisma: PrismaClient | undefined
}

// Database configuration for Resume Matcher
// Production: Use pooled connection for Render/Neon
// Development: Use direct connection
const getDatabaseUrl = () => {
  const DATABASE_URL = process.env.DATABASE_URL!
  const DATABASE_POOL_URL = process.env.DATABASE_POOL_URL
  
  if (!DATABASE_URL) {
    throw new Error('DATABASE_URL environment variable is required')
  }
  
  // Use pooled connection in production, direct in development
  const databaseUrl = process.env.NODE_ENV === 'production' && DATABASE_POOL_URL 
    ? DATABASE_POOL_URL 
    : DATABASE_URL
  
  // Ensure SSL is enabled for production PostgreSQL
  const urlWithSSL = databaseUrl.includes('sslmode') 
    ? databaseUrl 
    : `${databaseUrl}?sslmode=require`
    
  return urlWithSSL
}

// Create Prisma client with Resume Matcher optimizations
const createPrismaClient = () => {
  return new PrismaClient({
    datasources: {
      db: {
        url: getDatabaseUrl()
      }
    },
    log: process.env.NODE_ENV === 'development' 
      ? ['query', 'error', 'warn'] 
      : ['error'],
  })
}

// Singleton pattern for Prisma client
const prisma = globalThis.__prisma ?? createPrismaClient()

if (process.env.NODE_ENV !== 'production') {
  globalThis.__prisma = prisma
}

export { prisma }

// Credit system utilities for Resume Matcher
export const creditQueries = {
  // Get user with current balance
  async getUserWithBalance(userId: number) {
    return prisma.user.findUnique({
      where: { id: userId },
      select: {
        id: true,
        email: true,
        name: true,
        credits_balance: true,
        stripeCustomerId: true,
      }
    })
  },

  // Get transaction history for user
  async getTransactionHistory(userId: number, limit = 50) {
    return prisma.creditTransaction.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
      take: limit,
      select: {
        id: true,
        delta_credits: true,
        reason: true,
        meta: true,
        createdAt: true,
      }
    })
  },

  // Atomic credit transaction with balance update
  async createCreditTransaction(data: {
    userId: number
    delta_credits: number
    reason: string
    stripeEventId?: string
    meta?: any
  }) {
    return prisma.$transaction(async (tx) => {
      // Create transaction record
      const transaction = await tx.creditTransaction.create({
        data: {
          userId: data.userId,
          delta_credits: data.delta_credits,
          reason: data.reason as any,
          stripeEventId: data.stripeEventId,
          meta: data.meta,
        }
      })

      // Update user balance
      await tx.user.update({
        where: { id: data.userId },
        data: {
          credits_balance: {
            increment: data.delta_credits
          }
        }
      })

      return transaction
    })
  },

  // Check if Stripe event already processed (idempotency)
  async isStripeEventProcessed(stripeEventId: string) {
    const existing = await prisma.creditTransaction.findUnique({
      where: { stripeEventId }
    })
    return !!existing
  }
}

export default prisma