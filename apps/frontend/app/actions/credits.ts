'use server'

import { auth } from '@/auth'
import { creditUtils, resumeMatcherCredits, CreditSystemError } from '@/lib/utils/credits'
import { stripeUtils, CREDIT_PACKAGES } from '@/lib/stripe'
import { prisma } from '@/lib/prisma'
import { redact, resumeMatcherRedaction } from '@/lib/utils/redaction'
import { redirect } from 'next/navigation'

// Resume Matcher Server Actions for Credit System

// Purchase credits action
export async function purchaseCredits(formData: FormData) {
  const requestId = `action_purchase_${Date.now()}`
  
  try {
    // Authenticate user
    const session = await auth()
    if (!session?.user?.email || !session.user.id) {
      console.warn(`[${requestId}] Unauthorized purchase attempt`)
      throw new CreditSystemError('Authentication required', 'UNAUTHORIZED', 401)
    }

    // Extract form data
    const priceId = formData.get('priceId') as string
    const quantity = parseInt(formData.get('quantity') as string || '1', 10)
    const locale = formData.get('locale') as string || 'en'

    if (!priceId || isNaN(quantity) || quantity < 1) {
      console.warn(`[${requestId}] Invalid purchase parameters`, {
        priceId: priceId ? redact(priceId, 'generic') : 'missing',
        quantity,
        user: { email: redact(session.user.email, 'email') }
      })
      throw new CreditSystemError('Invalid parameters', 'INVALID_PARAMETERS', 400)
    }

    // Validate credit package
    const creditPackage = stripeUtils.getCreditPackage(priceId)
    if (!creditPackage) {
      console.warn(`[${requestId}] Invalid price ID`, {
        priceId: redact(priceId, 'generic'),
        user: { email: redact(session.user.email, 'email') }
      })
      throw new CreditSystemError('Invalid price ID', 'INVALID_PRICE_ID', 400)
    }

    // Get or create user in database
    let user = await prisma.user.findUnique({
      where: { email: session.user.email },
      select: {
        id: true,
        email: true,
        name: true,
        stripeCustomerId: true
      }
    })

    if (!user) {
      console.info(`[${requestId}] Creating new user for purchase`, {
        email: redact(session.user.email, 'email')
      })
      
      user = await prisma.user.create({
        data: {
          email: session.user.email,
          name: session.user.name || null,
        },
        select: {
          id: true,
          email: true,
          name: true,
          stripeCustomerId: true
        }
      })
    }

    // Get or create Stripe customer
    let stripeCustomerId = user.stripeCustomerId
    
    if (!stripeCustomerId) {
      console.info(`[${requestId}] Creating Stripe customer`, {
        userId: redact(user.id.toString(), 'userId'),
        email: redact(user.email, 'email')
      })
      
      const customer = await stripeUtils.createCustomer({
        email: user.email,
        name: user.name || undefined,
        userId: user.id
      })

      stripeCustomerId = customer.id

      // Update user with Stripe customer ID
      await prisma.user.update({
        where: { id: user.id },
        data: { stripeCustomerId }
      })
    }

    // Create checkout session
    const totalCredits = creditPackage.credits * quantity
    const checkoutSession = await stripeUtils.createCheckoutSession({
      priceId,
      quantity,
      customerId: stripeCustomerId,
      locale,
      metadata: {
        userId: user.id.toString(),
        credits: totalCredits.toString(),
        package: creditPackage.id,
        requestId
      }
    })

    console.info(`[${requestId}] Purchase checkout created`, {
      sessionId: redact(checkoutSession.id, 'generic'),
      user: resumeMatcherRedaction.user({
        id: user.id,
        email: user.email,
        name: user.name ?? undefined // Convert null to undefined
      }),
      package: creditPackage.name,
      credits: totalCredits,
      quantity
    })

    // Redirect to Stripe checkout
    redirect(checkoutSession.url!)

  } catch (error) {
    console.error(`[${requestId}] Purchase action failed`, {
      error: error instanceof Error ? error.message : 'Unknown error'
    })

    if (error instanceof CreditSystemError) {
      throw error
    }

    throw new CreditSystemError(
      'Purchase failed',
      'PURCHASE_FAILED',
      500
    )
  }
}

// Spend credits for resume analysis
export async function spendCreditsForResumeAnalysis(metadata: {
  resumeId?: string
  analysisType?: string
} = {}) {
  const requestId = `action_spend_analysis_${Date.now()}`
  
  try {
    // Authenticate user
    const session = await auth()
    if (!session?.user?.id) {
      throw new CreditSystemError('Authentication required', 'UNAUTHORIZED', 401)
    }

    const userId = parseInt(session.user.id, 10)
    if (isNaN(userId)) {
      throw new CreditSystemError('Invalid user ID', 'INVALID_USER_ID', 400)
    }

    // Check if user can afford resume analysis
    const canAfford = await resumeMatcherCredits.canAnalyzeResume(userId)
    if (!canAfford) {
      console.warn(`[${requestId}] Insufficient credits for resume analysis`, {
        userId: redact(userId.toString(), 'userId'),
        required: creditUtils.getCreditCost('resume_analysis')
      })
      throw new CreditSystemError(
        'Insufficient credits for resume analysis',
        'INSUFFICIENT_CREDITS',
        402
      )
    }

    // Spend credits
    const result = await resumeMatcherCredits.spendForResumeAnalysis(userId, metadata)

    console.info(`[${requestId}] Credits spent for resume analysis`, {
      userId: redact(userId.toString(), 'userId'),
      cost: creditUtils.getCreditCost('resume_analysis'),
      newBalance: result.newBalance,
      metadata: metadata.resumeId ? { resumeId: redact(metadata.resumeId, 'generic') } : {}
    })

    return {
      success: true,
      newBalance: result.newBalance,
      cost: creditUtils.getCreditCost('resume_analysis')
    }

  } catch (error) {
    console.error(`[${requestId}] Resume analysis spending failed`, {
      error: error instanceof Error ? error.message : 'Unknown error'
    })

    if (error instanceof CreditSystemError) {
      throw error
    }

    throw new CreditSystemError(
      'Failed to spend credits for resume analysis',
      'SPEND_FAILED',
      500
    )
  }
}

// Spend credits for job matching
export async function spendCreditsForJobMatch(metadata: {
  jobId?: string
  matchType?: string
} = {}) {
  const requestId = `action_spend_job_match_${Date.now()}`
  
  try {
    // Authenticate user
    const session = await auth()
    if (!session?.user?.id) {
      throw new CreditSystemError('Authentication required', 'UNAUTHORIZED', 401)
    }

    const userId = parseInt(session.user.id, 10)
    if (isNaN(userId)) {
      throw new CreditSystemError('Invalid user ID', 'INVALID_USER_ID', 400)
    }

    // Check if user can afford job matching
    const canAfford = await resumeMatcherCredits.canMatchJob(userId)
    if (!canAfford) {
      console.warn(`[${requestId}] Insufficient credits for job matching`, {
        userId: redact(userId.toString(), 'userId'),
        required: creditUtils.getCreditCost('job_match')
      })
      throw new CreditSystemError(
        'Insufficient credits for job matching',
        'INSUFFICIENT_CREDITS',
        402
      )
    }

    // Spend credits
    const result = await resumeMatcherCredits.spendForJobMatch(userId, metadata)

    console.info(`[${requestId}] Credits spent for job matching`, {
      userId: redact(userId.toString(), 'userId'),
      cost: creditUtils.getCreditCost('job_match'),
      newBalance: result.newBalance,
      metadata: metadata.jobId ? { jobId: redact(metadata.jobId, 'generic') } : {}
    })

    return {
      success: true,
      newBalance: result.newBalance,
      cost: creditUtils.getCreditCost('job_match')
    }

  } catch (error) {
    console.error(`[${requestId}] Job match spending failed`, {
      error: error instanceof Error ? error.message : 'Unknown error'
    })

    if (error instanceof CreditSystemError) {
      throw error
    }

    throw new CreditSystemError(
      'Failed to spend credits for job matching',
      'SPEND_FAILED',
      500
    )
  }
}

// Spend credits for resume improvement
export async function spendCreditsForResumeImprovement(metadata: {
  resumeId?: string
  improvementType?: string
} = {}) {
  const requestId = `action_spend_improvement_${Date.now()}`
  
  try {
    // Authenticate user
    const session = await auth()
    if (!session?.user?.id) {
      throw new CreditSystemError('Authentication required', 'UNAUTHORIZED', 401)
    }

    const userId = parseInt(session.user.id, 10)
    if (isNaN(userId)) {
      throw new CreditSystemError('Invalid user ID', 'INVALID_USER_ID', 400)
    }

    // Check if user can afford resume improvement
    const canAfford = await resumeMatcherCredits.canImproveResume(userId)
    if (!canAfford) {
      console.warn(`[${requestId}] Insufficient credits for resume improvement`, {
        userId: redact(userId.toString(), 'userId'),
        required: creditUtils.getCreditCost('resume_improvement')
      })
      throw new CreditSystemError(
        'Insufficient credits for resume improvement',
        'INSUFFICIENT_CREDITS',
        402
      )
    }

    // Spend credits
    const result = await resumeMatcherCredits.spendForResumeImprovement(userId, metadata)

    console.info(`[${requestId}] Credits spent for resume improvement`, {
      userId: redact(userId.toString(), 'userId'),
      cost: creditUtils.getCreditCost('resume_improvement'),
      newBalance: result.newBalance,
      metadata: metadata.resumeId ? { resumeId: redact(metadata.resumeId, 'generic') } : {}
    })

    return {
      success: true,
      newBalance: result.newBalance,
      cost: creditUtils.getCreditCost('resume_improvement')
    }

  } catch (error) {
    console.error(`[${requestId}] Resume improvement spending failed`, {
      error: error instanceof Error ? error.message : 'Unknown error'
    })

    if (error instanceof CreditSystemError) {
      throw error
    }

    throw new CreditSystemError(
      'Failed to spend credits for resume improvement',
      'SPEND_FAILED',
      500
    )
  }
}

// Get user credit summary
export async function getUserCreditSummary() {
  const requestId = `action_summary_${Date.now()}`
  
  try {
    // Authenticate user
    const session = await auth()
    if (!session?.user?.id) {
      throw new CreditSystemError('Authentication required', 'UNAUTHORIZED', 401)
    }

    const userId = parseInt(session.user.id, 10)
    if (isNaN(userId)) {
      throw new CreditSystemError('Invalid user ID', 'INVALID_USER_ID', 400)
    }

    // Get credit summary
    const summary = await creditUtils.getCreditSummary(userId)

    console.info(`[${requestId}] Credit summary retrieved`, {
      userId: redact(userId.toString(), 'userId'),
      balance: summary.balance,
      transactionCount: summary.recentTransactions.length
    })

    return {
      success: true,
      balance: summary.balance,
      recentTransactions: summary.recentTransactions,
      packages: CREDIT_PACKAGES.map(pkg => ({
        id: pkg.id,
        name: pkg.name,
        credits: pkg.credits,
        price: stripeUtils.formatPrice(pkg.priceInCents),
        description: pkg.description,
        popular: pkg.popular,
        stripePriceId: pkg.stripePriceId
      })),
      costs: {
        resume_analysis: creditUtils.getCreditCost('resume_analysis'),
        job_match: creditUtils.getCreditCost('job_match'),
        resume_improvement: creditUtils.getCreditCost('resume_improvement')
      }
    }

  } catch (error) {
    console.error(`[${requestId}] Credit summary retrieval failed`, {
      error: error instanceof Error ? error.message : 'Unknown error'
    })

    if (error instanceof CreditSystemError) {
      throw error
    }

    throw new CreditSystemError(
      'Failed to get credit summary',
      'SUMMARY_FAILED',
      500
    )
  }
}
