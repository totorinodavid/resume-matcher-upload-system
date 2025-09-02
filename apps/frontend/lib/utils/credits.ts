import { prisma, creditQueries } from '@/lib/prisma'
import { CREDIT_COSTS } from '@/lib/stripe'

// Resume Matcher Credit System Errors
export class CreditSystemError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 400
  ) {
    super(message)
    this.name = 'CreditSystemError'
  }
}

// Credit operation types for Resume Matcher
export type CreditReason = 
  | 'purchase'
  | 'refund' 
  | 'resume_analysis'
  | 'job_match'
  | 'resume_improvement'
  | 'manual'
  | 'bonus'
  | 'welcome'

// Credit transaction interface
export interface CreditTransaction {
  userId: number
  amount: number
  reason: CreditReason
  metadata?: Record<string, any>
  stripeEventId?: string
}

// Credit balance interface for UI
export interface CreditBalance {
  current: number
  pending?: number
  lastUpdated: Date
}

// Credit utilities for Resume Matcher
export const creditUtils = {
  // Check if user has sufficient credits for operation
  async hasCredits(userId: number, requiredAmount: number): Promise<boolean> {
    const user = await creditQueries.getUserWithBalance(userId)
    if (!user) {
      throw new CreditSystemError('User not found', 'USER_NOT_FOUND', 404)
    }
    return user.credits_balance >= requiredAmount
  },

  // Get credit cost for Resume Matcher features
  getCreditCost(feature: keyof typeof CREDIT_COSTS): number {
    return CREDIT_COSTS[feature]
  },

  // Spend credits for Resume Matcher features
  async spendCredits(params: {
    userId: number
    amount: number
    reason: CreditReason
    metadata?: Record<string, any>
  }): Promise<{ success: boolean; newBalance: number }> {
    try {
      // Check if user has sufficient credits
      const hasEnough = await this.hasCredits(params.userId, params.amount)
      if (!hasEnough) {
        throw new CreditSystemError(
          'Insufficient credits',
          'INSUFFICIENT_CREDITS',
          402
        )
      }

      // Create negative transaction (spending)
      await creditQueries.createCreditTransaction({
        userId: params.userId,
        delta_credits: -params.amount,
        reason: params.reason,
        meta: params.metadata,
      })

      // Get updated balance
      const user = await creditQueries.getUserWithBalance(params.userId)
      
      return {
        success: true,
        newBalance: user?.credits_balance || 0
      }
    } catch (error) {
      if (error instanceof CreditSystemError) {
        throw error
      }
      throw new CreditSystemError(
        'Failed to spend credits',
        'CREDIT_SPEND_FAILED',
        500
      )
    }
  },

  // Add credits (purchases, bonuses, etc.)
  async addCredits(params: {
    userId: number
    amount: number
    reason: CreditReason
    stripeEventId?: string
    metadata?: Record<string, any>
  }): Promise<{ success: boolean; newBalance: number }> {
    try {
      // Check for duplicate Stripe events (idempotency)
      if (params.stripeEventId) {
        const isProcessed = await creditQueries.isStripeEventProcessed(params.stripeEventId)
        if (isProcessed) {
          // Event already processed, return current balance
          const user = await creditQueries.getUserWithBalance(params.userId)
          return {
            success: true,
            newBalance: user?.credits_balance || 0
          }
        }
      }

      // Create positive transaction (adding)
      await creditQueries.createCreditTransaction({
        userId: params.userId,
        delta_credits: params.amount,
        reason: params.reason,
        stripeEventId: params.stripeEventId,
        meta: params.metadata,
      })

      // Get updated balance
      const user = await creditQueries.getUserWithBalance(params.userId)

      return {
        success: true,
        newBalance: user?.credits_balance || 0
      }
    } catch (error) {
      if (error instanceof CreditSystemError) {
        throw error
      }
      throw new CreditSystemError(
        'Failed to add credits',
        'CREDIT_ADD_FAILED',
        500
      )
    }
  },

  // Get user's credit balance and recent transactions
  async getCreditSummary(userId: number): Promise<{
    balance: number
    recentTransactions: Array<{
      id: string
      amount: number
      reason: string
      createdAt: Date
      metadata?: any
    }>
  }> {
    try {
      const [user, transactions] = await Promise.all([
        creditQueries.getUserWithBalance(userId),
        creditQueries.getTransactionHistory(userId, 10)
      ])

      if (!user) {
        throw new CreditSystemError('User not found', 'USER_NOT_FOUND', 404)
      }

      return {
        balance: user.credits_balance,
        recentTransactions: transactions.map(tx => ({
          id: tx.id.toString(),
          amount: tx.delta_credits,
          reason: tx.reason,
          createdAt: tx.createdAt,
          metadata: tx.meta
        }))
      }
    } catch (error) {
      if (error instanceof CreditSystemError) {
        throw error
      }
      throw new CreditSystemError(
        'Failed to get credit summary',
        'CREDIT_SUMMARY_FAILED',
        500
      )
    }
  },

  // Calculate refund amount for Stripe refunds
  calculateRefundCredits(
    originalAmount: number,
    refundAmount: number,
    originalCredits: number
  ): number {
    // Proportional refund calculation
    const refundRatio = refundAmount / originalAmount
    return Math.floor(originalCredits * refundRatio)
  },

  // Validate credit operation for Resume Matcher
  validateCreditOperation(
    operation: 'spend' | 'add',
    amount: number,
    reason: CreditReason
  ): { valid: boolean; error?: string } {
    // Validate amount
    if (!Number.isInteger(amount) || amount <= 0) {
      return { valid: false, error: 'Amount must be a positive integer' }
    }

    // Validate spending limits
    if (operation === 'spend' && amount > 1000) {
      return { valid: false, error: 'Cannot spend more than 1000 credits at once' }
    }

    // Validate adding limits
    if (operation === 'add' && amount > 10000) {
      return { valid: false, error: 'Cannot add more than 10000 credits at once' }
    }

    // Validate reason for spending
    if (operation === 'spend') {
      const spendReasons = ['resume_analysis', 'job_match', 'resume_improvement', 'manual']
      if (!spendReasons.includes(reason)) {
        return { valid: false, error: 'Invalid spending reason' }
      }
    }

    return { valid: true }
  }
}

// Helper functions for Resume Matcher features
export const resumeMatcherCredits = {
  // Check if user can perform resume analysis
  async canAnalyzeResume(userId: number): Promise<boolean> {
    const cost = creditUtils.getCreditCost('resume_analysis')
    return creditUtils.hasCredits(userId, cost)
  },

  // Check if user can perform job matching
  async canMatchJob(userId: number): Promise<boolean> {
    const cost = creditUtils.getCreditCost('job_match')
    return creditUtils.hasCredits(userId, cost)
  },

  // Check if user can improve resume
  async canImproveResume(userId: number): Promise<boolean> {
    const cost = creditUtils.getCreditCost('resume_improvement')
    return creditUtils.hasCredits(userId, cost)
  },

  // Spend credits for resume analysis
  async spendForResumeAnalysis(
    userId: number,
    metadata: { resumeId?: string; analysisType?: string } = {}
  ) {
    const cost = creditUtils.getCreditCost('resume_analysis')
    return creditUtils.spendCredits({
      userId,
      amount: cost,
      reason: 'resume_analysis',
      metadata
    })
  },

  // Spend credits for job matching
  async spendForJobMatch(
    userId: number,
    metadata: { jobId?: string; matchType?: string } = {}
  ) {
    const cost = creditUtils.getCreditCost('job_match')
    return creditUtils.spendCredits({
      userId,
      amount: cost,
      reason: 'job_match',
      metadata
    })
  },

  // Spend credits for resume improvement
  async spendForResumeImprovement(
    userId: number,
    metadata: { resumeId?: string; improvementType?: string } = {}
  ) {
    const cost = creditUtils.getCreditCost('resume_improvement')
    return creditUtils.spendCredits({
      userId,
      amount: cost,
      reason: 'resume_improvement',
      metadata
    })
  }
}

export default creditUtils