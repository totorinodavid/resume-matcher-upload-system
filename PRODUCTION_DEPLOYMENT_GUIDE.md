# 🚀 PRODUCTION DEPLOYMENT GUIDE
## Resume Matcher - Vollständige Produktionsumstellung

### 📋 ÜBERSICHT
Diese Anleitung führt durch die **vollständige Umstellung von Development auf Production** für das Resume Matcher System mit allen kritischen Konfigurationen.

---

## ⚠️ KRITISCHE PRODUCTION CHECKLIST

### 🔐 1. SECURITY & AUTHENTICATION
```bash
# ✅ ERFORDERLICH: Sichere Secrets generieren
NEXTAUTH_SECRET="[64-char-random-string]"
SESSION_SECRET_KEY="[64-char-random-string]"

# ✅ ERFORDERLICH: Production URLs setzen
NEXTAUTH_URL="https://your-production-domain.com"
ALLOWED_ORIGINS='["https://your-production-domain.com","https://www.your-production-domain.com"]'
```

### 💳 2. STRIPE CONFIGURATION
```bash
# ✅ KRITISCH: Live Stripe Keys verwenden
STRIPE_SECRET_KEY="sk_live_..." # NICHT sk_test_!
STRIPE_WEBHOOK_SECRET="whsec_..." # Live webhook secret

# ✅ KRITISCH: Live Price IDs setzen
STRIPE_PRICE_SMALL_ID="price_live_small"
STRIPE_PRICE_MEDIUM_ID="price_live_medium" 
STRIPE_PRICE_LARGE_ID="price_live_large"

# ✅ KRITISCH: Credits-Mapping konfigurieren
STRIPE_PRICE_SMALL_CREDITS="100"
STRIPE_PRICE_MEDIUM_CREDITS="500"
STRIPE_PRICE_LARGE_CREDITS="1500"
```

### 🗄️ 3. DATABASE CONFIGURATION
```bash
# ✅ KRITISCH: Production PostgreSQL
DATABASE_URL="postgresql://user:pass@production-host:5432/production_db"
ASYNC_DATABASE_URL="postgresql+asyncpg://user:pass@production-host:5432/production_db"

# ✅ ERFORDERLICH: Connection pooling
DB_POOL_SIZE="20"
DB_MAX_OVERFLOW="30"
```

### 🤖 4. AI PROVIDER CONFIGURATION
```bash
# ✅ ERFORDERLICH: Production AI Keys
OPENAI_API_KEY="sk-proj-..." # Production OpenAI key
LLM_PROVIDER="openai"
LLM_MODEL="gpt-4o-mini" # Oder gpt-4o für bessere Qualität

# ✅ OPTIONAL: Alternative AI providers
# ANTHROPIC_API_KEY="sk-ant-..."
# GOOGLE_API_KEY="..."
```

---

## 🔧 DEPLOYMENT KONFIGURATION

### 📦 1. RENDER.COM PRODUCTION SETUP

**render.yaml Production Config:**
```yaml
services:
  - name: resume-matcher-backend-production
    type: web
    runtime: docker
    plan: starter # Upgrade von free für Production!
    numInstances: 2 # Load balancing
    
    # Production domains
    domains:
      - your-api-domain.com
    
    # SSL/HTTPS enforcement
    httpsOnly: true
    
    # Health monitoring
    healthCheckPath: /healthz
    healthCheckInterval: 30
    healthCheckTimeout: 10
    healthCheckThreshold: 3
    
    # Production environment variables
    envVars:
      - key: ENV
        value: production
      - key: LOG_LEVEL
        value: info
      - key: DEBUG
        value: "false"
```

### 🌐 2. VERCEL PRODUCTION SETUP

**vercel.json Production Config:**
```json
{
  "name": "resume-matcher-production",
  "domains": ["your-domain.com", "www.your-domain.com"],
  "env": {
    "NODE_ENV": "production",
    "NEXT_PUBLIC_APP_URL": "https://your-domain.com",
    "NEXT_PUBLIC_API_URL": "https://your-api-domain.com"
  },
  "build": {
    "env": {
      "NODE_ENV": "production"
    }
  }
}
```

---

## 🚨 KRITISCHE MIGRATION SCHRITTE

### 📊 1. STRIPE MIGRATION (WICHTIGSTE PUNKTE!)

#### A) Stripe Dashboard Konfiguration
```bash
# 🌐 https://dashboard.stripe.com

# 1. ✅ Live Mode aktivieren (Toggle oben rechts)
# 2. ✅ Live API Keys kopieren:
#    - Publishable key: pk_live_...
#    - Secret key: sk_live_...

# 3. ✅ Webhooks konfigurieren:
#    URL: https://your-api-domain.com/
#    Events: checkout.session.completed, invoice.payment_succeeded
#    Secret: whsec_... (Live webhook secret)

# 4. ✅ Products & Prices erstellen:
#    - Small Package: 100 Credits
#    - Medium Package: 500 Credits  
#    - Large Package: 1500 Credits
```

#### B) Price ID Mapping
```bash
# ✅ KRITISCH: Live Price IDs aus Stripe Dashboard kopieren
STRIPE_PRICE_SMALL_ID="price_1ABC..." # Live price ID
STRIPE_PRICE_MEDIUM_ID="price_1DEF..." # Live price ID
STRIPE_PRICE_LARGE_ID="price_1GHI..." # Live price ID
```

#### C) Webhook URL Update
```bash
# ✅ KRITISCH: Webhook URL in Stripe setzen
# Alte URL: https://resume-matcher-backend-j06k.onrender.com/
# Neue URL: https://your-api-domain.com/

# ⚠️ WICHTIG: Emergency Route funktioniert bei "/"
```

### 🔄 2. DATABASE MIGRATION

#### A) Backup erstellen
```sql
-- Development backup
pg_dump $DEV_DATABASE_URL > backup_dev_$(date +%Y%m%d).sql

-- Production restore (nach DB setup)
psql $PROD_DATABASE_URL < backup_dev_20250901.sql
```

#### B) Alembic Migration
```bash
# Production migration
cd apps/backend
uv run alembic upgrade head

# Verify migration
uv run alembic current
uv run alembic history
```

### 🔐 3. SECURITY HARDENING

#### A) Environment Variables Audit
```bash
# ✅ ALLE Secrets rotiert für Production:
- NEXTAUTH_SECRET ✅
- SESSION_SECRET_KEY ✅  
- STRIPE_SECRET_KEY ✅
- STRIPE_WEBHOOK_SECRET ✅
- DATABASE_URL ✅
- OPENAI_API_KEY ✅

# ❌ ENTFERNEN in Production:
- DEBUG=false
- E2E_TEST_MODE="" (leer lassen)
- DISABLE_AUTH_FOR_TESTS="" (leer lassen)
```

#### B) CORS & Origins
```bash
# ✅ KRITISCH: Nur Production domains erlauben
ALLOWED_ORIGINS='["https://your-domain.com","https://www.your-domain.com"]'

# ❌ ENTFERNEN:
# "http://localhost:3000"
# "*.vercel.app" (nur für staging)
```

---

## 📊 MONITORING & LOGGING

### 🔍 1. LOG-LEVEL KONFIGURATION
```bash
# Production logging
LOG_LEVEL="info"  # Nicht "debug"!
PYTHONUNBUFFERED="1"

# Structured logging für Production
ENABLE_STRUCTURED_LOGS="true"
LOG_FORMAT="json"
```

### 📈 2. HEALTH MONITORING
```bash
# Health check endpoints überwachen:
GET /healthz -> {"status":"ok","database":"ok"}

# Critical endpoints:
POST / -> Stripe webhooks
GET /api/v1/me/credits -> Credits API

# Error rates überwachen:
- 4xx errors < 5%
- 5xx errors < 1%
- Response time < 2s
```

### 🚨 3. ALERT SETUP
```bash
# Render Dashboard Alerts konfigurieren:
- Service down
- High error rate
- Memory usage > 80%
- Response time > 5s

# Stripe Webhook Monitoring:
- Failed webhook deliveries
- Signature validation errors
```

---

## 🧪 PRODUCTION TESTING PROTOCOL

### 💳 1. STRIPE LIVE TESTING
```bash
# ⚠️ VORSICHT: Live payments mit echtem Geld!

# Test sequence:
1. ✅ Small purchase (100 credits)
2. ✅ Check credit balance update
3. ✅ Verify webhook logs
4. ✅ Database credit_ledger entry
5. ✅ Stripe Dashboard payment confirmed

# Test mit Cent-Beträgen für Validierung
```

### 🔧 2. SYSTEM INTEGRATION TEST
```bash
# End-to-end flow:
1. ✅ User registration
2. ✅ Authentication 
3. ✅ Resume upload
4. ✅ Credit purchase
5. ✅ Credit consumption
6. ✅ Resume processing
7. ✅ Results delivery

# Performance test:
- Concurrent users: 50+
- Response time: <2s
- Error rate: <1%
```

---

## 🔄 ROLLBACK STRATEGIE

### ⏪ 1. EMERGENCY ROLLBACK
```bash
# Render: Previous deployment rollback
# Dashboard -> Deployments -> Revert

# Vercel: Git-based rollback  
git revert [commit-hash]
vercel --prod

# Database: Schema rollback
uv run alembic downgrade -1
```

### 📞 2. INCIDENT RESPONSE
```bash
# Priority 1: Payment processing down
1. Check Stripe webhook deliveries
2. Verify backend health status
3. Check database connectivity
4. Review recent deployments

# Priority 2: Credit processing issues
1. Check stripe_webhook logs
2. Verify credit_ledger entries
3. Check user balance updates
4. Review webhook payload processing
```

---

## 📚 PRODUCTION CHECKLISTS

### 🚀 PRE-DEPLOYMENT CHECKLIST
- [ ] ✅ Alle Secrets rotiert
- [ ] ✅ Live Stripe keys konfiguriert
- [ ] ✅ Production database setup
- [ ] ✅ Webhook URLs aktualisiert
- [ ] ✅ CORS origins gesetzt
- [ ] ✅ Environment variables validiert
- [ ] ✅ SSL certificates aktiv
- [ ] ✅ Monitoring configured
- [ ] ✅ Backup strategy implementiert
- [ ] ✅ Rollback plan getestet

### 🔍 POST-DEPLOYMENT CHECKLIST  
- [ ] ✅ Health checks passing
- [ ] ✅ Stripe webhooks funktional
- [ ] ✅ Credit purchases arbeiten
- [ ] ✅ Database migrations erfolgreich
- [ ] ✅ Logs strukturiert und sauber
- [ ] ✅ Performance metrics normal
- [ ] ✅ Error rates niedrig
- [ ] ✅ User authentication funktional
- [ ] ✅ Resume processing arbeitet
- [ ] ✅ All integrations aktiv

### 🎯 24H MONITORING CHECKLIST
- [ ] ✅ Payment success rate >95%
- [ ] ✅ Webhook delivery rate >99%
- [ ] ✅ API response time <2s
- [ ] ✅ Error rate <1%
- [ ] ✅ Database connection stable
- [ ] ✅ Credit balance accuracy
- [ ] ✅ User satisfaction scores
- [ ] ✅ No security incidents

---

## 🆘 SUPPORT & TROUBLESHOOTING

### 📞 KRITISCHE KONTAKTE
```bash
# Render Support: support@render.com
# Vercel Support: support@vercel.com  
# Stripe Support: support@stripe.com

# Internal escalation:
# Level 1: Backend issues
# Level 2: Payment processing
# Level 3: Data integrity
```

### 🔧 COMMON PRODUCTION ISSUES

#### 1. "Credits not added after payment"
```bash
# Debug steps:
1. Check Stripe Dashboard -> Webhooks -> Attempts
2. Verify webhook URL: https://your-api-domain.com/
3. Check Render logs for webhook processing
4. Verify database credit_ledger entries
5. Check user_id mapping accuracy
```

#### 2. "Backend not responding"
```bash
# Debug steps:
1. Check Render service status
2. Verify health endpoint: /healthz
3. Check database connectivity
4. Review resource usage
5. Check recent deployments
```

#### 3. "Authentication failures"
```bash
# Debug steps:
1. Verify NEXTAUTH_SECRET set correctly
2. Check NEXTAUTH_URL matches domain
3. Verify JWT token validity
4. Check session configuration
5. Review CORS settings
```

---

## 📈 PERFORMANCE OPTIMIZATION

### ⚡ 1. BACKEND OPTIMIZATION
```bash
# Production settings:
WEB_CONCURRENCY="4"  # Render workers
DB_POOL_SIZE="20"    # Connection pool
CACHE_TTL="3600"     # 1 hour cache

# Resource limits:
MEMORY_LIMIT="1GB"   # Render plan
CPU_LIMIT="1 vCPU"   # Render plan
```

### 🌐 2. FRONTEND OPTIMIZATION
```bash
# Next.js production config:
output: 'standalone'
compress: true
poweredByHeader: false

# Image optimization:
images: {
  domains: ['your-domain.com'],
  formats: ['image/webp', 'image/avif']
}
```

---

## 🎉 PRODUCTION LAUNCH PROTOKOLL

### 🚀 LAUNCH DAY CHECKLIST
1. **T-24h:** Final testing in staging
2. **T-12h:** Database backup & migration  
3. **T-6h:** Secret rotation & configuration
4. **T-2h:** Staging freeze & final verification
5. **T-0h:** Production deployment
6. **T+1h:** Smoke tests & monitoring
7. **T+24h:** Performance review & optimization

### 📊 SUCCESS METRICS
- **Payment Success Rate:** >95%
- **API Response Time:** <2s (p95)
- **Error Rate:** <1%
- **Uptime:** >99.9%
- **User Satisfaction:** >4.5/5

---

**🎯 PRODUCTION BEREIT!**

Mit dieser Konfiguration ist das Resume Matcher System vollständig production-ready mit:
- ✅ Sichere Stripe Live-Zahlungen
- ✅ Robuste Backend-Infrastructure  
- ✅ Vollständiges Monitoring
- ✅ Emergency-Rollback-Fähigkeit
- ✅ Performance-Optimierung

**Viel Erfolg mit dem Production Launch! 🚀**
