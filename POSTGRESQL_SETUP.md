# PostgreSQL Configuration for Production (Neon)

This document explains how to configure PostgreSQL with Neon for production deployment.

## 🔧 Configuration Steps

### 1. Environment Variables

Add these to your production environment (Vercel/Railway/etc.):

```bash
# Backend (.env)
SYNC_DATABASE_URL=postgresql+psycopg://username:password@host:5432/database?sslmode=require
ASYNC_DATABASE_URL=postgresql+asyncpg://username:password@host:5432/database

# Session security
SESSION_SECRET_KEY=your-production-session-secret-minimum-32-chars

# AI Configuration  
LLM_API_KEY=your-openai-api-key
EMBEDDING_API_KEY=your-openai-api-key
```

### 2. Neon Database Setup

1. **Create Neon Project**: Visit [neon.tech](https://neon.tech)
2. **Get Connection String**: Copy from Neon dashboard
3. **Update Environment**: Replace the example connection strings

### 3. Database Dependencies

The required dependencies are already installed:
- `psycopg2-binary==2.9.10` - PostgreSQL adapter
- `asyncpg` - Async PostgreSQL adapter (via SQLAlchemy)

### 4. Local Development

For local development, PostgreSQL is configured:
```bash
# Set this for local testing
E2E_TEST_MODE=1
```

### 5. Database Migration

The application automatically creates tables on startup:
```python
# In app/base.py - runs on startup
async with async_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

## ✅ Verification

Test database connection:
```bash
# Local with E2E mode
E2E_TEST_MODE=1 uv run python serve.py

# Production
uv run python serve.py
```

## 🚨 Important Notes

- **Production Mode**: Enforces PostgreSQL only
- **SSL Required**: Neon requires SSL connections
- **Connection Pooling**: Configured for serverless environments
- **Error Handling**: Graceful fallback and logging included
