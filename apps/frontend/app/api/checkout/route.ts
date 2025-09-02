import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/auth'
import { stripe, stripeUtils, CREDIT_PACKAGES } from '@/lib/stripe'
import { prisma } from '@/lib/prisma'
import { redact, resumeMatcherRedaction } from '@/lib/utils/redaction'

export const runtime = 'nodejs'

// Resume Matcher Checkout API
// Creates Stripe checkout session for credit purchases
export async function POST(request: NextRequest) {
  const requestId = `req_${Date.now()}_${Math.random().toString(36).substring(7)}`
  
  try {
    // Authenticate user
    const session = await auth()
    if (!session?.user?.email || !session.user.id) {
      console.warn(`[${requestId}] Unauthorized checkout attempt`)
      return NextResponse.json(
        {
          request_id: requestId,
          error: {
            code: 'UNAUTHORIZED',
            message: 'Authentication required',
            detail: null
          }
        },
        { status: 401 }
      )
    }

    // Parse request body
    const body = await request.json()
    const { priceId, quantity = 1, locale = 'en' } = body

    if (!priceId || !Number.isInteger(quantity) || quantity < 1) {
      console.warn(`[${requestId}] Invalid checkout parameters`, {
        priceId: priceId ? redact(priceId, 'generic') : 'missing',
        quantity,
        user: resumeMatcherRedaction.user({
          id: parseInt(session.user.id),
          email: session.user.email ?? undefined,
          name: session.user.name ?? undefined
        })
      })
      return NextResponse.json(
        {
          request_id: requestId,
          error: {
            code: 'INVALID_PARAMETERS',
            message: 'Invalid priceId or quantity',
            detail: 'priceId must be a valid string and quantity must be a positive integer'
          }
        },
        { status: 400 }
      )
    }

    // Validate credit package
    const creditPackage = stripeUtils.getCreditPackage(priceId)
    if (!creditPackage) {
      console.warn(`[${requestId}] Invalid price ID`, {
        priceId: redact(priceId, 'generic'),
        user: resumeMatcherRedaction.user({
          id: parseInt(session.user.id),
          email: session.user.email ?? undefined,
          name: session.user.name ?? undefined
        })
      })
      return NextResponse.json(
        {
          request_id: requestId,
          error: {
            code: 'INVALID_PRICE_ID',
            message: 'Invalid price ID',
            detail: 'The provided price ID is not recognized'
          }
        },
        { status: 400 }
      )
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
      console.info(`[${requestId}] Creating new user for checkout`, {
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

    console.info(`[${requestId}] Checkout session created`, {
      sessionId: redact(checkoutSession.id, 'generic'),
      user: resumeMatcherRedaction.user({
        id: user.id,
        email: user.email,
        name: user.name ?? undefined
      }),
      package: creditPackage.name,
      credits: totalCredits,
      quantity
    })

    return NextResponse.json({
      request_id: requestId,
      checkout_url: checkoutSession.url,
      session_id: checkoutSession.id,
      credits: totalCredits,
      package: {
        name: creditPackage.name,
        description: creditPackage.description,
        credits: creditPackage.credits,
        price: stripeUtils.formatPrice(creditPackage.priceInCents)
      }
    })

  } catch (error) {
    console.error(`[${requestId}] Checkout session creation failed`, {
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined
    })

    if (error instanceof Error && error.message.includes('Invalid API Key')) {
      return NextResponse.json(
        {
          request_id: requestId,
          error: {
            code: 'STRIPE_CONFIGURATION_ERROR',
            message: 'Payment system configuration error',
            detail: null
          }
        },
        { status: 500 }
      )
    }

    return NextResponse.json(
      {
        request_id: requestId,
        error: {
          code: 'CHECKOUT_CREATION_FAILED',
          message: 'Failed to create checkout session',
          detail: process.env.NODE_ENV === 'development' 
            ? error instanceof Error ? error.message : 'Unknown error'
            : null
        }
      },
      { status: 500 }
    )
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    service: 'resume-matcher-checkout',
    timestamp: new Date().toISOString()
  })
}
