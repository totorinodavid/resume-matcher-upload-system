import Stripe from 'stripe'

// Stripe configuration for Resume Matcher
if (!process.env.STRIPE_SECRET_KEY) {
  throw new Error('STRIPE_SECRET_KEY environment variable is required')
}

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2024-06-20',
  typescript: true,
})

// Resume Matcher Credit System Configuration
export const STRIPE_CONFIG = {
  // Webhook configuration
  webhookSecret: process.env.STRIPE_WEBHOOK_SECRET!,
  
  // Currency for Resume Matcher (EUR by default)
  currency: 'eur' as const,
  
  // Success/cancel URLs for checkout
  successUrl: (locale: string) => `${process.env.NEXTAUTH_URL}/${locale}/billing?success=true`,
  cancelUrl: (locale: string) => `${process.env.NEXTAUTH_URL}/${locale}/billing?canceled=true`,
}

// Credit packages for Resume Matcher
export const CREDIT_PACKAGES = [
  {
    id: 'starter',
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_SMALL || 'price_starter',
    name: 'Starter Pack',
    credits: 100,
    priceInCents: 500, // €5.00
    description: '10 resume analyses or 20 job matches',
    popular: false,
  },
  {
    id: 'pro',
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_MEDIUM || 'price_pro',
    name: 'Pro Pack', 
    credits: 500,
    priceInCents: 2000, // €20.00
    description: '50 resume analyses + improvements',
    popular: true,
  },
  {
    id: 'premium',
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_PRICE_LARGE || 'price_premium',
    name: 'Premium Pack',
    credits: 1200,
    priceInCents: 3500, // €35.00 (Best Value)
    description: 'Everything included with 20% bonus',
    popular: false,
  }
] as const

// Credit costs for Resume Matcher features
export const CREDIT_COSTS = {
  resume_analysis: 10,
  job_match: 5,
  resume_improvement: 15,
} as const

// Stripe error handling for Resume Matcher
export class StripeError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number = 400
  ) {
    super(message)
    this.name = 'StripeError'
  }
}

// Utility functions
export const stripeUtils = {
  // Format price for display
  formatPrice(priceInCents: number, currency = 'eur'): string {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(priceInCents / 100)
  },

  // Get credit package by price ID
  getCreditPackage(stripePriceId: string) {
    return CREDIT_PACKAGES.find(pkg => pkg.stripePriceId === stripePriceId)
  },

  // Validate webhook signature
  validateWebhookSignature(
    body: string | Buffer,
    signature: string,
    secret: string = STRIPE_CONFIG.webhookSecret
  ): Stripe.Event {
    try {
      return stripe.webhooks.constructEvent(body, signature, secret)
    } catch (error) {
      throw new StripeError(
        'Invalid webhook signature',
        'WEBHOOK_SIGNATURE_INVALID',
        400
      )
    }
  },

  // Create customer with Resume Matcher metadata
  async createCustomer(params: {
    email: string
    name?: string
    userId: number
  }): Promise<Stripe.Customer> {
    try {
      return await stripe.customers.create({
        email: params.email,
        name: params.name,
        metadata: {
          userId: params.userId.toString(),
          source: 'resume-matcher',
          created_at: new Date().toISOString(),
        }
      })
    } catch (error) {
      throw new StripeError(
        'Failed to create Stripe customer',
        'CUSTOMER_CREATION_FAILED',
        500
      )
    }
  },

  // Create checkout session for credit purchase
  async createCheckoutSession(params: {
    priceId: string
    quantity: number
    customerId: string
    locale: string
    metadata?: Record<string, string>
  }): Promise<Stripe.Checkout.Session> {
    try {
      const session = await stripe.checkout.sessions.create({
        customer: params.customerId,
        payment_method_types: ['card'],
        line_items: [
          {
            price: params.priceId,
            quantity: params.quantity,
          },
        ],
        mode: 'payment',
        success_url: STRIPE_CONFIG.successUrl(params.locale),
        cancel_url: STRIPE_CONFIG.cancelUrl(params.locale),
        metadata: {
          ...params.metadata,
          locale: params.locale,
          source: 'resume-matcher-credits',
        },
        // Auto-apply promotion codes
        allow_promotion_codes: true,
        // Collect billing address for compliance
        billing_address_collection: 'required',
      })

      return session
    } catch (error) {
      throw new StripeError(
        'Failed to create checkout session',
        'CHECKOUT_SESSION_CREATION_FAILED',
        500
      )
    }
  }
}

export default stripe