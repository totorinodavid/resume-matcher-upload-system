# Resume Matcher Credit System

A comprehensive Stripe-based credit system for the Resume Matcher platform, built with Next.js 15, Prisma, and PostgreSQL.

## Overview

The Resume Matcher Credit System enables users to purchase credits for premium features:
- **Resume Analysis** (-10 credits): Detailed ATS analysis and scoring
- **Job Matching** (-5 credits): Find matching job opportunities  
- **Resume Improvement** (-15 credits): AI-powered resume enhancements

## Architecture

### Tech Stack
- **Frontend**: Next.js 15 (App Router), TypeScript, Tailwind CSS 4
- **Backend**: Next.js API Routes, Prisma ORM
- **Database**: PostgreSQL (Neon/Render with connection pooling)
- **Payments**: Stripe with webhook verification
- **Auth**: NextAuth v5 integration
- **Internationalization**: next-intl (English/German)

### Key Features
- 🔒 **Secure**: Webhook signature verification, PII redaction in logs
- 💾 **Ledger-based**: All credit changes tracked in `CreditTransaction`
- 🔄 **Idempotent**: Duplicate Stripe events handled gracefully
- 📊 **Real-time**: Live balance updates and transaction history
- 🌍 **Multilingual**: Full German/English internationalization
- 🎨 **Modern UI**: Radix UI primitives with motion animations

## Database Schema

```sql
-- Users table (extended)
model User {
  id                Int                 @id @default(autoincrement())
  email             String              @unique
  name              String?
  stripeCustomerId  String?             @unique
  credits_balance   Int                 @default(0)
  creditTransactions CreditTransaction[]
}

-- Credit transaction ledger
model CreditTransaction {
  id              BigInt      @id @default(autoincrement())
  userId          Int
  delta_credits   Int         // Positive for additions, negative for spending
  reason          CreditReason
  stripeEventId   String?     @unique // For idempotency
  meta            Json?       // Additional metadata
  createdAt       DateTime    @default(now())
}

-- Local price cache
model Price {
  stripePriceId   String   @id
  creditsPerUnit  Int
  priceInCents    Int
  currency        String   @default("eur")
  active          Boolean  @default(true)
}
```

## Credit Packages

| Package | Credits | Price | Value per Credit | Best For |
|---------|---------|-------|------------------|----------|
| Starter | 100 | €5.00 | €0.050 | Trying out features |
| Pro | 500 | €20.00 | €0.040 | Regular users |
| Premium | 1200 | €35.00 | €0.029 | Power users (20% bonus) |

## API Routes

### `/api/checkout` (POST)
Creates Stripe checkout session for credit purchases.

**Request:**
```json
{
  "priceId": "price_1Xxxxxxx_starter",
  "quantity": 1,
  "locale": "en"
}
```

**Response:**
```json
{
  "request_id": "req_123",
  "checkout_url": "https://checkout.stripe.com/...",
  "session_id": "cs_test_...",
  "credits": 100,
  "package": {
    "name": "Starter Pack",
    "credits": 100,
    "price": "€5.00"
  }
}
```

### `/api/stripe/credits-webhook` (POST)
Processes Stripe webhook events for credit system.

**Supported Events:**
- `checkout.session.completed` - Add credits after successful payment
- `charge.refunded` / `refund.created` - Deduct credits proportionally
- `payment_intent.succeeded` - Additional verification

## Server Actions

### Credit Operations
```typescript
// Purchase credits (redirects to Stripe)
await purchaseCredits(formData)

// Spend credits for features
await spendCreditsForResumeAnalysis({ resumeId: "123" })
await spendCreditsForJobMatch({ jobId: "456" })
await spendCreditsForResumeImprovement({ resumeId: "123" })

// Get credit summary
const summary = await getUserCreditSummary()
```

### Error Handling
All actions use structured error handling:
```typescript
class CreditSystemError extends Error {
  constructor(message: string, public code: string, public statusCode: number)
}

// Error codes:
// - UNAUTHORIZED (401)
// - INSUFFICIENT_CREDITS (402)
// - INVALID_PARAMETERS (400)
// - CREDIT_SYSTEM_ERROR (500)
```

## UI Components

### CreditBalance
Displays current balance with feature costs and low balance warnings.

```tsx
<CreditBalance 
  locale="en"
  showHistory={true}
  className="w-full"
/>
```

### CreditPurchase
Interactive package selection with Stripe checkout integration.

```tsx
<CreditPurchase 
  locale="en"
  onPurchaseStart={() => console.log('Starting purchase')}
  onPurchaseError={(error) => console.error(error)}
/>
```

### CreditHistory
Transaction history with filtering, export, and detailed metadata.

```tsx
<CreditHistory 
  locale="en"
  showFilters={true}
  maxTransactions={50}
/>
```

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
DATABASE_POOL_URL=postgresql://user:pass@pooler:5432/db?sslmode=require&pgbouncer=true

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Credit Package Price IDs
NEXT_PUBLIC_STRIPE_PRICE_SMALL=price_1Xxxxxxx_starter
NEXT_PUBLIC_STRIPE_PRICE_MEDIUM=price_1Xxxxxxx_pro
NEXT_PUBLIC_STRIPE_PRICE_LARGE=price_1Xxxxxxx_premium

# Auth
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=your-secret-key
```

## Setup Instructions

### 1. Database Setup
```bash
# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate dev --name add_credit_system

# Seed initial data (optional)
npx prisma db seed
```

### 2. Stripe Configuration
```bash
# Install Stripe CLI
# Create products
stripe products create --name "Resume Matcher Credits"

# Create prices
stripe prices create \
  --product=prod_xxx \
  --unit-amount=500 \
  --currency=eur \
  --metadata.credits=100 \
  --metadata.package=starter

# Set up webhook endpoint
stripe listen --forward-to localhost:3000/api/stripe/credits-webhook
```

### 3. Development Workflow
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Test webhook locally
stripe trigger checkout.session.completed

# Run type checking
npm run type-check

# Run tests
npm run test
```

## Production Deployment

### Vercel Deployment
1. Set environment variables in Vercel dashboard
2. Configure Stripe webhook endpoint: `https://your-app.vercel.app/api/stripe/credits-webhook`
3. Use pooled database URL for optimal performance

### Render/Railway Deployment
1. Configure environment variables
2. Set up database with SSL support
3. Configure webhook endpoint with production URL

### Database Considerations
- Use connection pooling in production (Neon/PgBouncer)
- Enable SSL for all database connections
- Monitor connection limits and performance
- Regular backups of transaction data

## Security Features

### PII Redaction
All logging automatically redacts sensitive information:
```typescript
import { redact, resumeMatcherRedaction } from '@/lib/utils/redaction'

// Redact user info
console.log('User:', resumeMatcherRedaction.user(user))

// Redact individual fields
console.log('Email:', redact(email, 'email'))
console.log('Stripe ID:', redact(stripeId, 'stripe'))
```

### Webhook Security
- Signature verification for all Stripe events
- Raw body parsing to preserve signatures
- Request ID tracking for debugging
- Automatic retry handling with exponential backoff

### Database Security
- Parameterized queries prevent SQL injection
- Atomic transactions ensure data consistency
- Unique constraints prevent duplicate events
- SSL-only connections in production

## Monitoring & Observability

### Structured Logging
```typescript
console.info(`[${requestId}] Credits added successfully`, {
  user: resumeMatcherRedaction.user(user),
  credits: amount,
  newBalance: result.newBalance,
  eventId: redact(stripeEventId, 'generic')
})
```

### Error Tracking
- Sentry integration for production errors
- Request ID correlation across logs
- Performance monitoring for database queries
- Webhook event success/failure tracking

### Metrics to Monitor
- Credit purchase conversion rates
- Feature usage by credit cost
- Webhook processing latency
- Database connection pool usage
- Failed payment rates

## Testing

### Unit Tests
```bash
# Test credit utilities
npm run test -- credits.test.ts

# Test webhook processing
npm run test -- webhook.test.ts

# Test UI components
npm run test -- components/credit-*.test.tsx
```

### Integration Tests
```bash
# Test complete purchase flow
npm run test:e2e -- billing.spec.ts

# Test webhook processing with Stripe CLI
stripe trigger checkout.session.completed --add checkout_session:metadata.userId=123
```

### Load Testing
```bash
# Test webhook processing under load
npm run test:load -- webhook-load.ts

# Test database performance
npm run test:db -- credit-transactions.ts
```

## Troubleshooting

### Common Issues

**Webhook Signature Verification Failed**
- Check `STRIPE_WEBHOOK_SECRET` environment variable
- Verify raw body parsing in API route
- Ensure correct endpoint URL in Stripe dashboard

**Database Connection Issues**
- Check `DATABASE_URL` and `DATABASE_POOL_URL` variables
- Verify SSL configuration for production
- Monitor connection pool limits

**Credit Balance Mismatch**
- Check for duplicate webhook processing
- Verify transaction ledger consistency
- Run balance recalculation script if needed

**UI Components Not Loading**
- Check next-intl configuration
- Verify translation files are complete
- Check for client/server component mismatch

### Debugging Commands
```bash
# Check database schema
npx prisma db pull
npx prisma generate

# Verify Stripe webhook events
stripe events list --limit 10

# Test credit operations
npm run script:test-credits

# Check translation completeness
npm run script:check-translations
```

## Migration Guide

### From Existing System
1. Run database migration to add credit tables
2. Import existing user data
3. Set initial credit balances
4. Configure Stripe products and prices
5. Update frontend to use new components

### Version Updates
- Always run `npx prisma migrate deploy` after updates
- Check for breaking changes in Stripe API versions
- Update webhook signatures if Stripe SDK version changes
- Test all credit flows after deployment

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/credit-enhancement`
3. Follow TypeScript strict mode requirements
4. Add tests for new functionality
5. Update documentation as needed
6. Submit pull request with detailed description

## License

This credit system is part of the Resume Matcher project and follows the same license terms.

## Support

For issues related to the credit system:
1. Check this documentation
2. Review error logs with request IDs
3. Test with Stripe CLI in development
4. Contact support with specific error details and request IDs
