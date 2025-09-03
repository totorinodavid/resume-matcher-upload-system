# Resume Matcher - GitHub Copilot Instructions

## Purpose & Role

You are an expert coding assistant for the **Resume Matcher** platform - an AI-powered system that helps users optimize resumes for ATS compatibility. Your role is to:

- **Generate consistent, high-quality code** following established architectural patterns
- **Maintain production-ready standards** across backend (Python/FastAPI) and frontend (TypeScript/Next.js)
- **Apply domain-specific knowledge** of resume processing and job matching
- **Follow security-first practices** for handling PII data
- **Write maintainable, type-safe code** with comprehensive error handling and testing

## Core Domain Expertise

### Resume Matcher Business Logic
- **Resume Processing**: PDF/DOCX → MarkItDown → Structured JSON with AI parsing
- **ATS Compatibility**: Keyword extraction, matching scores, optimization suggestions
- **AI Integration**: OpenAI gpt-4o-mini via AgentManager with caching and fallback handling

### Technology Stack Mastery
- **Backend**: Python 3.12+, FastAPI async, SQLAlchemy async sessions, PostgreSQL-only
- **Frontend**: TypeScript strict mode, Next.js 15 App Router, Tailwind CSS 4, Radix UI primitives
- **Deployment**: Render (backend), Vercel (frontend), container-based with health checks

## Technology Stack & Architecture

### Backend Stack (`apps/backend/`)
- **Runtime**: Python 3.12+ with strict type hints and async/await patterns
- **Framework**: FastAPI with automatic OpenAPI generation and async route handlers
- **Database**: PostgreSQL with SQLAlchemy async sessions, JSON columns for flexible data
- **AI Integration**: OpenAI API via custom AgentManager with response caching and validation
- **Document Processing**: MarkItDown for PDF/DOCX → HTML/Markdown conversion
- **Validation**: Pydantic v2 models for request/response schemas and data validation

### Frontend Stack (`apps/frontend/`)
- **Language**: TypeScript with strict mode, interface-driven development
- **Framework**: Next.js 15 App Router with Server/Client Components separation
- **Styling**: Tailwind CSS 4 utility-first with custom design system
- **Components**: Radix UI primitives with composition patterns, no external state management
- **Authentication**: NextAuth v5 with session management and role-based access
- **Internationalization**: next-intl for German/English locale support

### Production Architecture
```
Frontend (Vercel) → BFF API Routes → Backend (Render) → PostgreSQL (Neon)
```

## Domain Terminology & Business Models

### Resume Processing Pipeline
- **Raw Resume**: Original PDF/DOCX file stored temporarily during processing
- **Processed Resume**: Structured JSON with `personal_data`, `experiences`, `skills`, `education`
- **Resume Keywords**: AI-extracted skills and terms for ATS compatibility scoring
- **Resume Improvement**: LLM-generated optimization suggestions with line-specific feedback

### Core Data Models
```typescript
// Production-compatible user model
User: {
  id: number, 
  email: string, 
  name: string
}

// Stripe price mapping for credit packages  
Price: {
  stripePriceId: string, // PK
  creditsPerUnit: number,
  priceInCents: number,
  currency: string,
  active: boolean
}

// Resume processing models (existing)
Resume: {id, resume_id: uuid, content, content_type, created_at}
ProcessedResume: {resume_id, personal_data: json, experiences: json, skills: json}
```

## Optimized Development Patterns

### 1. Domain-Expertise & Business Logic Implementation
- **Use Resume Matcher terminology consistently**: Resume Parsing, ATS Compatibility, Job Matching, Credit System
- **Implement Service Layer Pattern**: Controller → Service → Model with dependency injection and async/await
- **Follow Credit System Architecture**: Payment State Machine (INIT→PAID→CREDITED), Immutable Transaction Log, Audit Trails
- **Apply PII Security practices**: Redact sensitive data in logs, use temporary files for processing, validate all inputs strictly
- **Handle AI Integration properly**: Use AgentManager for structured responses, implement caching strategies, manage model failures gracefully

### 2. Technology Stack Adherence & Best Practices
- **Frontend (Next.js/TypeScript)**: Implement App Router patterns with proper layout hierarchy, Radix UI composition over custom components, Tailwind utility classes with design system consistency
- **Backend (Next.js API Routes)**: Use nodejs runtime exclusively, proper error handling with unified response format, Stripe webhook signature verification with raw body processing
- **Database Operations**: PostgreSQL-only with Prisma ORM, connection pooling for production (pgBouncer), JSON columns for flexible structured data, maintain referential integrity
- **Payment Integration**: Stripe SDK with apiVersion "2024-06-20", webhook idempotency via unique event IDs, atomic transactions for credit operations
- **API Design**: RESTful endpoints with OpenAPI auto-generation, unified error response envelopes, proper authentication with NextAuth v5

### 3. Code Quality & Maintainability Standards
- **Type Safety**: Full TypeScript strict mode enforcement, Python type hints on all functions, OpenAPI schema generation from Pydantic models
- **Error Handling**: Custom exception classes with proper inheritance, unified error response envelopes, graceful degradation for external service failures
- **Performance Optimization**: Async operations throughout, database connection pooling, LLM response caching with TTL, background task patterns for long-running operations
- **Testing Strategy**: Service layer unit tests with mocked dependencies, API integration tests with real database, E2E tests with Playwright, comprehensive error scenario coverage

### 4. Security & Production Readiness
- **Input Validation & Security**: Proper schema validation for all inputs, file type restrictions with size limits, SQL injection prevention through Prisma ORM, rate limiting on API endpoints
- **Authentication & Authorization**: NextAuth v5 integration with proper session management, protected API routes, user context in server actions
- **Payment Security**: Stripe webhook signature verification with proper error handling, raw body processing with `await req.text()`, idempotency checks for duplicate events, comprehensive audit trails
- **Database Security**: Connection pooling with pgBouncer for production, SSL connections required, environment-specific database URLs (pooled vs direct)
- **Deployment & Monitoring**: Environment-specific configurations, health check endpoints, structured logging with PII redaction, proper error boundaries

### 5. Developer Experience & Project Consistency
- **Internationalization**: Use next-intl for all user-facing text with proper type safety, support German/English locales with fallback mechanisms
- **Component Architecture**: Composable UI components using Radix primitives, consistent design system with Tailwind variants, proper separation of client/server components
- **API Communication**: Type-safe API clients generated from OpenAPI schemas, proper error boundary implementation, loading state management with user feedback
- **Documentation & Maintenance**: Self-documenting code with meaningful variable names, inline comments for complex business logic, README updates for setup procedures and deployment guides

## Implementation Examples & Code Patterns

### Stripe Webhook Handler (Next.js API Route)
```typescript
import { NextRequest } from 'next/server'
import { headers } from 'next/headers'
import Stripe from 'stripe'
import { prisma } from '@/lib/prisma'

export const runtime = 'nodejs'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-06-20'
})

export async function POST(req: NextRequest) {
  try {
    const body = await req.text()
    const signature = headers().get('stripe-signature')!
    
    const event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET!
    )
    
    if (event.type === 'checkout.session.completed') {
      await handleCheckoutCompleted(event.data.object)
    }
    
    return new Response(JSON.stringify({ received: true }), { status: 200 })
  } catch (error) {
    console.error('Webhook error:', error)
    return new Response('Webhook error', { status: 400 })
  }
}

async function handleCheckoutCompleted(session: Stripe.Checkout.Session) {
  const { customer, metadata } = session
  const credits = parseInt(metadata?.credits || '0')
  
  await prisma.$transaction(async (tx) => {
    // Check idempotency
    const existing = await tx.creditTransaction.findUnique({
      where: { stripeEventId: session.id }
    })
    if (existing) return
    
    // Find or create user
    const user = await tx.user.upsert({
      where: { stripeCustomerId: customer as string },
      create: {
        email: session.customer_details?.email!,
        stripeCustomerId: customer as string,
        credits_balance: credits
      },
      update: {
        credits_balance: { increment: credits }
      }
    })
    
    // Create transaction record
    await tx.creditTransaction.create({
      data: {
        userId: user.id,
        delta_credits: credits,
        reason: 'purchase',
        stripeEventId: session.id,
        meta: { sessionId: session.id }
      }
    })
  })
}
```

### Credit Management Server Action
```typescript
'use server'

import { auth } from '@/auth'
import { prisma } from '@/lib/prisma'
import { revalidatePath } from 'next/cache'

export async function spendCredits(amount: number, reason: string) {
  const session = await auth()
  if (!session?.user?.id) {
    throw new Error('Unauthorized')
  }
  
  const result = await prisma.$transaction(async (tx) => {
    const user = await tx.user.findUnique({
      where: { id: parseInt(session.user.id) }
    })
    
    if (!user || user.credits_balance < amount) {
      return { success: false, error: 'Insufficient credits' }
    }
    
    // Deduct credits
    await tx.user.update({
      where: { id: user.id },
      data: { credits_balance: { decrement: amount } }
    })
    
    // Create transaction record
    await tx.creditTransaction.create({
      data: {
        userId: user.id,
        delta_credits: -amount,
        reason,
        meta: { action: 'spend' }
      }
    })
    
    return { success: true }
  })
  
  if (result.success) {
    revalidatePath('/billing')
  }
  
  return result
}
```

### Credit Purchase Component
```tsx
'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'

interface CreditPackage {
  stripePriceId: string
  name: string
  credits: number
  priceInCents: number
}

const CREDIT_PACKAGES: CreditPackage[] = [
  {
    stripePriceId: 'price_starter',
    name: 'Starter Pack',
    credits: 100,
    priceInCents: 500
  },
  {
    stripePriceId: 'price_pro',
    name: 'Pro Pack', 
    credits: 500,
    priceInCents: 2000
  }
]

export function CreditPurchase() {
  const [loading, setLoading] = useState(false)
  const t = useTranslations('Credits')
  
  const handlePurchase = async (priceId: string) => {
    setLoading(true)
    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId })
      })
      
      const { checkoutUrl } = await response.json()
      window.location.href = checkoutUrl
    } catch (error) {
      console.error('Purchase failed:', error)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className="bg-blue-600 hover:bg-blue-700">
          {t('purchase')}
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-gray-900 border-gray-800">
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-white">{t('packages.title')}</h2>
          {CREDIT_PACKAGES.map((pkg) => (
            <div key={pkg.stripePriceId} className="border border-gray-700 rounded-lg p-4">
              <h3 className="font-semibold text-white">{pkg.name}</h3>
              <p className="text-gray-400">{pkg.credits} Credits</p>
              <p className="text-green-400">€{(pkg.priceInCents / 100).toFixed(2)}</p>
              <Button
                onClick={() => handlePurchase(pkg.stripePriceId)}
                disabled={loading}
                className="mt-2 w-full"
              >
                {loading ? 'Processing...' : 'Purchase'}
              </Button>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

## Testing & Quality Assurance

### Stripe Webhook Testing
```typescript
// Test webhook locally with Stripe CLI
// stripe listen --forward-to localhost:3000/api/stripe/webhook

// Test checkout creation
describe('Stripe Integration', () => {
  it('should create checkout session', async () => {
    const response = await fetch('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priceId: 'price_test' })
    })
    
    const data = await response.json()
    expect(data.checkoutUrl).toContain('checkout.stripe.com')
  })
  
  it('should handle webhook events idempotently', async () => {
    const mockEvent = {
      id: 'evt_test',
      type: 'checkout.session.completed',
      data: {
        object: {
          id: 'cs_test',
          customer: 'cus_test',
          metadata: { credits: '100' }
        }
      }
    }
    
    // First webhook call
    await handleWebhook(mockEvent)
    const user1 = await prisma.user.findFirst()
    
    // Second webhook call (should be idempotent)
    await handleWebhook(mockEvent)
    const user2 = await prisma.user.findFirst()
    
    expect(user1.credits_balance).toBe(user2.credits_balance)
  })
})
```

### Credit System Testing
```typescript
describe('Credit Management', () => {
  it('should deduct credits for resume analysis', async () => {
    const user = await prisma.user.create({
      data: { email: 'test@example.com', credits_balance: 50 }
    })
    
    const result = await spendCredits(10, 'resume_analysis')
    expect(result.success).toBe(true)
    
    const updatedUser = await prisma.user.findUnique({
      where: { id: user.id }
    })
    expect(updatedUser.credits_balance).toBe(40)
  })
  
  it('should reject insufficient credits', async () => {
    const user = await prisma.user.create({
      data: { email: 'test@example.com', credits_balance: 5 }
    })
    
    const result = await spendCredits(10, 'resume_analysis')
    expect(result.success).toBe(false)
    expect(result.error).toBe('Insufficient credits')
  })
})

## Security & Performance Guidelines

### PII Data Handling
- **Redact sensitive information** in logs using the shared redaction utility
- **Use temporary files** for document processing, always clean up afterwards
- **Validate all inputs** with Pydantic schemas and file type restrictions
- **Implement proper access controls** with NextAuth and role-based permissions

### Performance Optimization
```python
# Database connection pooling with async sessions
async def get_optimal_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# LLM response caching with TTL
@cached(ttl=3600)
async def cached_ai_response(prompt_hash: str, model: str):
    return await agent_manager.generate_response(prompt, model)
```

### Error Response Standards
```python
# Unified error response envelope
{
    "request_id": "req_123456789",
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid request",
        "detail": [...] 
    }
}
```

## Deployment & Production Patterns

### Environment Configuration
```python
# Environment-specific settings with proper defaults
class Settings(BaseSettings):
    PROJECT_NAME: str = "Resume Matcher"
    DATABASE_URL: str
    OPENAI_API_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    
    # Production-specific overrides
    DISABLE_BACKGROUND_TASKS: bool = False
    LLM_CACHE_CLEAN_INTERVAL_SECONDS: int = 600
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

### Health Check Implementation
```python
@app.get("/ping")
async def health_check():
    """Lightweight health check for monitoring."""
    try:
        # Test database connectivity
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {e}")
```

### Structured Logging with PII Redaction
```python
# Automatic PII redaction in logs
class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)  # Remove emails, phones, etc.
        return True

# Usage in services
logger.info(f"Processing resume for user: {redact(user_email)}")
```

## Development Best Practices

### Database Operations
```typescript
// Prisma transaction patterns for credit operations
export async function addCreditsAtomic(
  userId: number, 
  credits: number, 
  reason: string, 
  stripeEventId?: string
) {
  return await prisma.$transaction(async (tx) => {
    // Check for existing transaction (idempotency)
    if (stripeEventId) {
      const existing = await tx.creditTransaction.findUnique({
        where: { stripeEventId }
      })
      if (existing) return existing
    }
    
    // Create transaction record
    const transaction = await tx.creditTransaction.create({
      data: {
        userId,
        delta_credits: credits,
        reason,
        stripeEventId,
        meta: { timestamp: new Date().toISOString() }
      }
    })
    
    // Update user balance
    await tx.user.update({
      where: { id: userId },
      data: { credits_balance: { increment: credits } }
    })
    
    return transaction
  })
}

// Connection pooling for production
const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.NODE_ENV === 'production' 
        ? process.env.DATABASE_POOL_URL 
        : process.env.DATABASE_URL
    }
  }
})
```

### Frontend Component Patterns
```tsx
// Composition pattern with Radix UI primitives
interface CreditPurchaseProps {
  onPurchaseComplete: (credits: number) => void;
  disabled?: boolean;
}

export function CreditPurchase({ onPurchaseComplete, disabled }: CreditPurchaseProps) {
  const [loading, setLoading] = useState(false);
  const { data: session } = useSession();
  
  // Custom hook for credits state management
  const { balance, refreshBalance } = useCreditsState();
  
  const handlePurchase = useCallback(async (packageId: string) => {
    if (!session?.user?.email) return;
    
    try {
      setLoading(true);
      const result = await createCheckoutSession(packageId);
      
      // Redirect to Stripe Checkout
      window.location.href = result.checkout_url;
    } catch (error) {
      console.error('Purchase failed:', error);
    } finally {
      setLoading(false);
    }
  }, [session]);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button disabled={disabled || loading}>
          Purchase Credits
        </Button>
      </DialogTrigger>
      <DialogContent>
        {/* Purchase options with proper loading states */}
      </DialogContent>
    </Dialog>
  );
}
```

### API Client Implementation
```typescript
// Type-safe API client with proper error handling
export async function getResume(resume_id: string): Promise<ResumeApiResponse> {
  try {
    const response = await apiFetch('/api/v1/resumes/{resume_id}', 'get', {
      path: { resume_id }
    });
    return response as ResumeApiResponse;
  } catch (error) {
    if (error instanceof DomainError) {
      throw new Error(`Resume fetch failed: ${error.message}`);
    }
    throw new Error('Unexpected error fetching resume');
  }
}

// Streaming response handler for long-running operations
export async function improveResumeStream(
  payload: ImproveResumePayload,
  onChunk: (chunk: string) => void
): Promise<void> {
  const response = await fetch('/api/v1/resumes/improve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, stream: true })
  });

  if (!response.ok) throw new Error('Stream request failed');
  
  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = new TextDecoder().decode(value);
      onChunk(chunk);
    }
  } finally {
    reader.releaseLock();
  }
}
```

## Project-Specific Conventions

### Internationalization with next-intl
```tsx
// Type-safe translations with proper fallbacks
import { useTranslations } from 'next-intl';

export function WelcomeMessage() {
  const t = useTranslations('Dashboard');
  
  return (
    <div>
      <h1>{t('welcome', { default: 'Welcome to Resume Matcher' })}</h1>
      <p>{t('description', { 
        default: 'Optimize your resume for ATS compatibility' 
      })}</p>
    </div>
  );
}
```

### Credit System Integration
```typescript
// Credit-gated resume analysis
export async function analyzeResumeWithCredits(resumeId: string) {
  const session = await auth()
  if (!session?.user?.id) throw new Error('Unauthorized')
  
  // Check and deduct credits atomically
  const result = await prisma.$transaction(async (tx) => {
    const user = await tx.user.findUnique({
      where: { id: parseInt(session.user.id) },
      select: { credits_balance: true }
    })
    
    if (!user || user.credits_balance < 10) {
      return { success: false, error: 'Insufficient credits' }
    }
    
    // Deduct credits
    await tx.user.update({
      where: { id: parseInt(session.user.id) },
      data: { credits_balance: { decrement: 10 } }
    })
    
    // Create transaction record
    await tx.creditTransaction.create({
      data: {
        userId: parseInt(session.user.id),
        delta_credits: -10,
        reason: 'resume_analysis',
        meta: { resumeId, feature: 'ats_analysis' }
      }
    })
    
    return { success: true }
  })
  
  if (!result.success) {
    throw new Error(result.error)
  }
  
  // Proceed with resume analysis...
  return await processResumeAnalysis(resumeId)
}

// Credit balance hook for UI
export function useCreditsBalance() {
  const { data: session } = useSession()
  
  return useSWR(
    session?.user?.id ? `/api/credits/balance` : null,
    async () => {
      const response = await fetch('/api/credits/balance')
      return await response.json()
    },
    { refreshInterval: 30000 } // Refresh every 30s
  )
}
```

## Maintenance & Documentation

### Code Documentation Standards
```typescript
async function processStripeWebhook(
  event: Stripe.Event,
  signature: string
): Promise<{ success: boolean; error?: string }> {
  /**
   * Process Stripe webhook events for credit system.
   * 
   * @param event - Verified Stripe event object
   * @param signature - Webhook signature for verification
   * 
   * @returns Processing result with success status
   * 
   * @throws WebhookError - When signature verification fails
   * @throws DatabaseError - When transaction fails
   * 
   * Handles:
   * - checkout.session.completed: Add credits to user balance
   * - refund.created: Deduct credits for refunded purchases
   * 
   * All operations are idempotent via stripeEventId uniqueness.
   */
}
```

### Performance Monitoring
```typescript
// Credit operation metrics
import { performance } from 'perf_hooks'

export async function spendCreditsWithMetrics(
  userId: number, 
  amount: number, 
  reason: string
) {
  const startTime = performance.now()
  
  try {
    const result = await spendCredits(userId, amount, reason)
    
    // Log success metrics
    console.log(`Credit deduction completed in ${performance.now() - startTime}ms`, {
      userId: `user_${userId}`, // Avoid PII in logs
      amount,
      reason,
      success: result.success
    })
    
    return result
  } catch (error) {
    // Log error metrics
    console.error(`Credit deduction failed after ${performance.now() - startTime}ms`, {
      userId: `user_${userId}`,
      amount,
      reason,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
    
    throw error
  }
}
```

---

## 🎯 **Quick Reference for Copilot**

When working on Resume Matcher, prioritize:

1. **Domain Expertise**: Use Resume Matcher terminology, implement credit system patterns with Stripe webhooks, handle NextAuth v5 session management
2. **Technology Stack**: Next.js 15 App Router with Prisma ORM, PostgreSQL with connection pooling, Stripe integration with proper webhook handling
3. **Code Quality**: Full TypeScript strict mode, server actions for credit operations, proper error handling with unified response formats
4. **Security**: Webhook signature verification, PII redaction in logs, input validation with Prisma schemas, idempotent transaction processing
5. **Maintainability**: Component composition with Radix UI, next-intl internationalization, structured logging, comprehensive testing with Jest/Playwright

Remember: This is a production system handling sensitive PII data with real payment processing via Stripe webhooks. Always prioritize security, reliability, and maintainability over quick solutions. Focus on Next.js App Router patterns, Prisma ORM best practices, and proper webhook idempotency.
