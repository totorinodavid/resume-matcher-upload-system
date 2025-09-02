import { NextRequest, NextResponse } from 'next/server'
import { headers } from 'next/headers'
import { stripe, stripeUtils, STRIPE_CONFIG } from '@/lib/stripe'
import { creditUtils } from '@/lib/utils/credits'
import { prisma } from '@/lib/prisma'
import { redact, resumeMatcherRedaction } from '@/lib/utils/redaction'
import type Stripe from 'stripe'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'
export const revalidate = 0
export const fetchCache = 'force-no-store'
export const maxDuration = 30

// Resume Matcher Frontend Credit System Webhook Handler
// Processes Stripe events for frontend credit system
export async function POST(request: NextRequest) {
  const requestId = `webhook_credits_${Date.now()}_${Math.random().toString(36).substring(7)}`
  
  try {
    // Get raw body for signature verification
    const body = await request.text()
    const headersList = await headers()
    const signature = headersList.get('stripe-signature')

    if (!signature) {
      console.warn(`[${requestId}] Missing Stripe signature`)
      return NextResponse.json(
        {
          request_id: requestId,
          error: {
            code: 'MISSING_SIGNATURE',
            message: 'Stripe signature required',
            detail: null
          }
        },
        { status: 400 }
      )
    }

    // Verify webhook signature
    let event: Stripe.Event
    try {
      event = stripeUtils.validateWebhookSignature(body, signature)
    } catch (error) {
      console.error(`[${requestId}] Invalid webhook signature`, {
        error: error instanceof Error ? error.message : 'Unknown error'
      })
      return NextResponse.json(
        {
          request_id: requestId,
          error: {
            code: 'WEBHOOK_SIGNATURE_INVALID',
            message: 'Invalid signature',
            detail: null
          }
        },
        { status: 400 }
      )
    }

    console.info(`[${requestId}] Processing Stripe webhook`, {
      event: resumeMatcherRedaction.stripeEvent({
        id: event.id,
        type: event.type,
        created: event.created,
        data: event.data
      })
    })

    // Process different event types
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(event, requestId)
        break

      case 'payment_intent.succeeded':
        await handlePaymentSucceeded(event, requestId)
        break

      case 'charge.refunded':
      case 'refund.created':
        await handleRefund(event, requestId)
        break

      case 'customer.subscription.created':
      case 'customer.subscription.updated':
      case 'customer.subscription.deleted':
        // Future: Handle subscription events for Resume Matcher Pro
        console.info(`[${requestId}] Subscription event received (not implemented)`, {
          eventType: event.type
        })
        break

      default:
        console.info(`[${requestId}] Unhandled webhook event type`, {
          eventType: event.type
        })
    }

    // Return success response quickly (Stripe requirement)
    return NextResponse.json(
      {
        request_id: requestId,
        status: 'received',
        event_type: event.type
      },
      { status: 200 }
    )

  } catch (error) {
    console.error(`[${requestId}] Webhook processing failed`, {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    })

    return NextResponse.json(
      {
        request_id: requestId,
        error: {
          code: 'WEBHOOK_PROCESSING_FAILED',
          message: 'Internal server error',
          detail: null
        }
      },
      { status: 500 }
    )
  }
}

// Handle successful checkout completion
async function handleCheckoutCompleted(event: Stripe.Event, requestId: string) {
  const session = event.data.object as Stripe.Checkout.Session

  if (session.payment_status !== 'paid') {
    console.warn(`[${requestId}] Checkout session not paid`, {
      sessionId: redact(session.id, 'generic'),
      paymentStatus: session.payment_status
    })
    return
  }

  // Extract user information
  const userId = session.metadata?.userId
  const creditsStr = session.metadata?.credits
  const packageId = session.metadata?.package

  if (!userId || !creditsStr) {
    console.error(`[${requestId}] Missing required metadata in checkout session`, {
      sessionId: redact(session.id, 'generic'),
      hasUserId: !!userId,
      hasCredits: !!creditsStr
    })
    return
  }

  const credits = parseInt(creditsStr, 10)
  const userIdNum = parseInt(userId, 10)

  if (isNaN(credits) || isNaN(userIdNum) || credits <= 0) {
    console.error(`[${requestId}] Invalid metadata values`, {
      sessionId: redact(session.id, 'generic'),
      credits,
      userId: userIdNum
    })
    return
  }

  // Find or create user
  let user = await prisma.user.findUnique({
    where: { id: userIdNum },
    select: { id: true, email: true, name: true, stripeCustomerId: true }
  })

  if (!user && session.customer_details?.email) {
    // Create user if doesn't exist (edge case)
    console.info(`[${requestId}] Creating user from checkout session`, {
      email: redact(session.customer_details.email, 'email'),
      sessionId: redact(session.id, 'generic')
    })
    
    user = await prisma.user.create({
      data: {
        email: session.customer_details.email,
        name: session.customer_details.name || null,
        stripeCustomerId: session.customer as string || null
      },
      select: { id: true, email: true, name: true, stripeCustomerId: true }
    })
  }

  if (!user) {
    console.error(`[${requestId}] User not found and cannot create`, {
      userId: redact(userIdNum.toString(), 'userId'),
      sessionId: redact(session.id, 'generic')
    })
    return
  }

  // Add credits to user account
  try {
    const result = await creditUtils.addCredits({
      userId: user.id,
      amount: credits,
      reason: 'purchase',
      stripeEventId: event.id,
      metadata: {
        sessionId: session.id,
        packageId,
        paymentIntentId: session.payment_intent,
        amountTotal: session.amount_total,
        currency: session.currency
      }
    })

    console.info(`[${requestId}] Credits added successfully`, {
      user: resumeMatcherRedaction.user({
        id: user.id,
        email: user.email,
        name: user.name ?? undefined
      }),
      credits,
      newBalance: result.newBalance,
      sessionId: redact(session.id, 'generic'),
      eventId: redact(event.id, 'generic')
    })

  } catch (error) {
    console.error(`[${requestId}] Failed to add credits`, {
      user: resumeMatcherRedaction.user({
        id: user.id,
        email: user.email,
        name: user.name ?? undefined
      }),
      credits,
      error: error instanceof Error ? error.message : 'Unknown error',
      sessionId: redact(session.id, 'generic')
    })
  }
}

// Handle successful payment (additional verification)
async function handlePaymentSucceeded(event: Stripe.Event, requestId: string) {
  const paymentIntent = event.data.object as Stripe.PaymentIntent

  console.info(`[${requestId}] Payment succeeded`, {
    paymentIntentId: redact(paymentIntent.id, 'generic'),
    amount: paymentIntent.amount,
    currency: paymentIntent.currency,
    customerId: paymentIntent.customer ? redact(paymentIntent.customer as string, 'stripe') : null
  })

  // Additional verification logic can be added here
  // For Resume Matcher, the main processing happens in checkout.session.completed
}

// Handle refunds
async function handleRefund(event: Stripe.Event, requestId: string) {
  const refund = event.data.object as Stripe.Refund

  // Find the original charge and associated user
  const charge = await stripe.charges.retrieve(refund.charge as string, {
    expand: ['customer']
  })

  if (!charge.customer) {
    console.warn(`[${requestId}] Refund without customer`, {
      refundId: redact(refund.id, 'generic'),
      chargeId: redact(charge.id, 'generic')
    })
    return
  }

  const customer = charge.customer as Stripe.Customer
  const user = await prisma.user.findUnique({
    where: { stripeCustomerId: customer.id },
    select: { id: true, email: true, name: true, credits_balance: true }
  })

  if (!user) {
    console.error(`[${requestId}] User not found for refund`, {
      customerId: redact(customer.id, 'stripe'),
      refundId: redact(refund.id, 'generic')
    })
    return
  }

  // Calculate refund credits
  const originalAmount = charge.amount
  const refundAmount = refund.amount
  
  // Find original credit transaction to determine original credits
  const originalTransaction = await prisma.creditTransaction.findFirst({
    where: {
      userId: user.id,
      reason: 'purchase',
      meta: {
        path: ['paymentIntentId'],
        equals: typeof charge.payment_intent === 'string' 
          ? charge.payment_intent 
          : (charge.payment_intent?.id ?? '')
      }
    },
    select: { delta_credits: true, meta: true }
  })

  if (!originalTransaction) {
    console.warn(`[${requestId}] Original transaction not found for refund`, {
      user: resumeMatcherRedaction.user({
        id: user.id,
        email: user.email,
        name: user.name ?? undefined
      }),
      refundId: redact(refund.id, 'generic')
    })
    return
  }

  const originalCredits = originalTransaction.delta_credits
  const refundCredits = creditUtils.calculateRefundCredits(
    originalAmount,
    refundAmount,
    originalCredits
  )

  // Deduct credits for refund
  try {
    const result = await creditUtils.addCredits({
      userId: user.id,
      amount: -refundCredits, // Negative amount for refund
      reason: 'refund',
      stripeEventId: event.id,
      metadata: {
        refundId: refund.id,
        chargeId: charge.id,
        originalAmount,
        refundAmount,
        originalCredits,
        refundCredits
      }
    })

    console.info(`[${requestId}] Credits refunded successfully`, {
      user: resumeMatcherRedaction.user({
        id: user.id,
        email: user.email,
        name: user.name ?? undefined
      }),
      refundCredits,
      newBalance: result.newBalance,
      refundId: redact(refund.id, 'generic')
    })

  } catch (error) {
    console.error(`[${requestId}] Failed to process refund`, {
      user: resumeMatcherRedaction.user({
        id: user.id,
        email: user.email,
        name: user.name ?? undefined
      }),
      refundCredits,
      error: error instanceof Error ? error.message : 'Unknown error',
      refundId: redact(refund.id, 'generic')
    })
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    service: 'resume-matcher-credit-webhook',
    timestamp: new Date().toISOString()
  })
}
