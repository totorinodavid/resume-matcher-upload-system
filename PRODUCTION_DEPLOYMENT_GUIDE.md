# 🚀 Production Deployment Guide with Neon PostgreSQL

## Prerequisites
- Neon account (https://neon.tech)
- Production domain ready
- Google OAuth credentials configured
- Stripe account (if using payments)

## Step 1: Set up Neon PostgreSQL Database

### 1.1 Create Neon Project
1. Go to https://neon.tech and sign in
2. Click "Create Project"
3. Choose your region (closest to your users)
4. Name your project: `resume-matcher-production`
5. Wait for database creation

### 1.2 Get Database Connection String
1. In your Neon dashboard, go to "Connection Details"
2. Select "Pooled connection" for production
3. Copy the connection string format:
   ```
   postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/main?sslmode=require
   ```

### 1.3 Update Backend Production Environment
Replace in `apps/backend/.env.production`:
```bash
DATABASE_URL=postgresql://your-username:your-password@your-host.neon.tech/main?sslmode=require
NEON_DATABASE_URL=postgresql://your-username:your-password@your-host.neon.tech/main?sslmode=require
```

## Step 2: Configure Frontend Production Environment

### 2.1 Update Frontend Production Environment
Replace in `apps/frontend/.env.production`:
```bash
# Your production domain
NEXT_PUBLIC_SITE_URL=https://your-domain.com
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com

# Google OAuth (get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-client-secret

# Clerk (get from Clerk dashboard)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-production-publishable-key
CLERK_SECRET_KEY=your-production-secret-key

# Stripe (get from Stripe dashboard)
STRIPE_SECRET_KEY=sk_live_your-production-key
NEXT_PUBLIC_STRIPE_PRICE_SMALL=price_your-small-plan
NEXT_PUBLIC_STRIPE_PRICE_MEDIUM=price_your-medium-plan
NEXT_PUBLIC_STRIPE_PRICE_LARGE=price_your-large-plan
```

## Step 3: Database Migration

### 3.1 Run Database Migrations
```bash
cd apps/backend
uv run alembic upgrade head
```

### 3.2 Verify Database Setup
```bash
# Test connection
uv run python -c "
from app.core.database import SessionLocal
from app.models import User
with SessionLocal() as db:
    print('Database connection successful!')
    print(f'Tables created: {db.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'\").scalar()}')
"
```

## Step 4: Production Deployment

### 4.1 Build Applications
```bash
# Backend
cd apps/backend
uv sync --frozen
uv run python -m pytest  # Run tests

# Frontend  
cd apps/frontend
npm ci
npm run build
npm run start  # Test production build
```

### 4.2 Deploy to Your Platform

**For Vercel (Frontend):**
1. Connect your GitHub repo to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy from `apps/frontend` directory

**For Railway/Render (Backend):**
1. Connect your GitHub repo
2. Set environment variables
3. Deploy from `apps/backend` directory
4. Set start command: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Step 5: Post-Deployment Verification

### 5.1 Health Checks
- Backend: `https://your-backend-domain.com/healthz`
- Frontend: `https://your-frontend-domain.com`

### 5.2 Test Core Functionality
1. User registration/login
2. Resume upload and parsing
3. Job matching functionality
4. Payment processing (if enabled)

## Security Checklist ✅

- [ ] Production AUTH_SECRET generated and set
- [ ] Database uses SSL (sslmode=require)
- [ ] CORS configured for production domains only
- [ ] Environment variables secured
- [ ] Google OAuth configured for production domain
- [ ] Stripe webhooks configured (if using payments)
- [ ] HTTPS enabled on all domains
- [ ] Security headers configured

## Troubleshooting

### Common Issues:
1. **Database Connection Failed**: Check Neon connection string and SSL settings
2. **Auth Errors**: Verify AUTH_SECRET and OAuth credentials
3. **CORS Issues**: Update CORS_ORIGINS in backend .env.production
4. **Build Failures**: Ensure all environment variables are set

### Neon-Specific:
- Use pooled connections for production
- Monitor connection limits in Neon dashboard
- Set up database backups in Neon settings

---

**🎯 Your Resume Matcher is now production-ready with Neon PostgreSQL!**
