# Resume Matcher Credit System - Deployment Guide

## 🚀 Quick Start Deployment

### Prerequisites
- ✅ Node.js 18+ and npm/yarn installed
- ✅ PostgreSQL database (Neon/Render recommended)
- ✅ Stripe account with API keys
- ✅ Next.js 15 project setup

### 1. Database Setup

**Run the migration:**
```bash
# Copy the migration file to your migrations folder
cp prisma/migrations/001_add_credit_system.sql ./migrations/

# Run against your database (adjust connection details)
psql $DATABASE_URL -f migrations/001_add_credit_system.sql

# Or using Prisma
npx prisma db push
npx prisma generate
```

### 2. Environment Configuration

**Add to your `.env.local`:**
```env
# Database
DATABASE_URL="postgresql://user:password@host:5432/database?sslmode=require"
DIRECT_URL="postgresql://user:password@host:5432/database?sslmode=require"

# Stripe
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# Credit Package Price IDs (will be generated)
NEXT_PUBLIC_STRIPE_PRICE_SMALL="price_..."
NEXT_PUBLIC_STRIPE_PRICE_MEDIUM="price_..."
NEXT_PUBLIC_STRIPE_PRICE_LARGE="price_..."

# NextAuth
NEXTAUTH_SECRET="your-secret-here"
NEXTAUTH_URL="http://localhost:3000"
```

### 3. Stripe Configuration

**Install Stripe CLI:**
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Windows (PowerShell)
scoop install stripe

# Or download from https://stripe.com/docs/stripe-cli
```

**Login and setup:**
```bash
# Login to Stripe
stripe login

# Setup products and prices
cd apps/frontend
npm install stripe
node scripts/setup-stripe.js

# Setup webhook forwarding for development
stripe listen --forward-to localhost:3000/api/stripe/credits-webhook
```

### 4. Install Dependencies

```bash
# Install required packages
npm install @stripe/stripe-js stripe @prisma/client

# Install UI dependencies (if not already installed)
npm install @radix-ui/react-dialog @radix-ui/react-select
npm install lucide-react framer-motion

# Install internationalization (if not already installed)
npm install next-intl
```

### 5. Development Testing

**Start development server:**
```bash
npm run dev
```

**Test the credit system:**
1. Navigate to `/billing` 
2. Purchase credits using Stripe test cards
3. Check database for credit transactions
4. Test resume analysis features with credits

**Test cards:**
- Success: `4242 4242 4242 4242`
- Declined: `4000 0000 0000 0002`
- More test cards: https://stripe.com/docs/testing

### 6. Production Deployment

**Render.com setup:**
```bash
# Add environment variables in Render dashboard
# Set up webhook endpoint: https://your-app.onrender.com/api/stripe/credits-webhook
```

**Neon.tech setup:**
```bash
# Use Neon connection string in DATABASE_URL
# Enable connection pooling for production
```

**Stripe production:**
```bash
# Switch to live keys in environment variables
# Update webhook endpoint in Stripe Dashboard
# Events to listen for:
# - checkout.session.completed
# - charge.refunded  
# - refund.created
```

---

## 🧪 Testing Checklist

### ✅ Database Tests
- [ ] Migration runs successfully
- [ ] Tables created with proper indexes
- [ ] Credit balance calculation works
- [ ] Transaction logging works

### ✅ Stripe Integration Tests  
- [ ] Checkout session creation
- [ ] Webhook signature verification
- [ ] Credit addition on payment success
- [ ] Refund handling

### ✅ UI Component Tests
- [ ] Credit balance display
- [ ] Package selection
- [ ] Purchase flow
- [ ] Transaction history
- [ ] Internationalization (DE/EN)

### ✅ Feature Integration Tests
- [ ] Resume analysis credit deduction
- [ ] Job matching credit deduction  
- [ ] Low balance warnings
- [ ] Insufficient credits handling

---

## 🔧 Troubleshooting

### Database Issues
```bash
# Check connection
npx prisma db pull

# Reset database (development only)
npx prisma migrate reset
```

### Stripe Issues
```bash
# Test webhook locally
stripe listen --forward-to localhost:3000/api/stripe/credits-webhook

# Check webhook events
stripe events list --limit=10
```

### Credit System Issues
```bash
# Check credit balance manually
psql $DATABASE_URL -c "SELECT id, email, credit_balance FROM users WHERE email = 'user@example.com';"

# Check transactions
psql $DATABASE_URL -c "SELECT * FROM credit_transactions ORDER BY created_at DESC LIMIT 10;"
```

---

## 📊 Monitoring & Analytics

### Key Metrics to Track
- Daily credit purchases
- Credit consumption by feature
- User credit balance distribution
- Conversion from free to paid credits

### Database Queries for Analytics
```sql
-- Daily credit purchases
SELECT DATE(created_at) as date, SUM(credits) as total_credits_purchased
FROM credit_transactions 
WHERE type = 'PURCHASE' 
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Most popular features
SELECT reason, COUNT(*) as usage_count, SUM(credits) as total_credits
FROM credit_transactions 
WHERE type = 'SPEND'
GROUP BY reason
ORDER BY usage_count DESC;

-- User segmentation by credits
SELECT 
  CASE 
    WHEN credit_balance = 0 THEN 'No Credits'
    WHEN credit_balance < 50 THEN 'Low Credits'  
    WHEN credit_balance < 200 THEN 'Medium Credits'
    ELSE 'High Credits'
  END as segment,
  COUNT(*) as user_count
FROM users 
GROUP BY segment;
```

---

## 🔒 Security Considerations

### Implemented Security Features
- ✅ Webhook signature verification
- ✅ PII redaction in logs
- ✅ SQL injection prevention (Prisma)
- ✅ Rate limiting considerations
- ✅ Input validation and sanitization

### Additional Security Recommendations
- Set up CORS properly for production
- Implement request rate limiting
- Monitor for unusual credit usage patterns
- Regular security audits of dependencies

---

## 📚 Documentation Links

- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Next.js 15 App Router](https://nextjs.org/docs/app)
- [Prisma Documentation](https://www.prisma.io/docs)
- [NextAuth.js v5](https://authjs.dev/getting-started)
- [next-intl Documentation](https://next-intl-docs.vercel.app)

---

**🎉 Your Resume Matcher Credit System is now ready for production!**

For support or questions, refer to the troubleshooting section above or check the implementation files in your project.
