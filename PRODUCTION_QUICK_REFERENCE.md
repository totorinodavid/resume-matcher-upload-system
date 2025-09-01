# ⚡ PRODUCTION QUICK REFERENCE
## Resume Matcher - Kritische Production-Einstellungen

### 🚨 STRIPE LIVE MIGRATION - KRITISCH!

```bash
# ✅ 1. Stripe Dashboard: Live Mode aktivieren
# https://dashboard.stripe.com -> Toggle "View test data" OFF

# ✅ 2. Live API Keys ersetzen
STRIPE_SECRET_KEY="sk_live_..." # NICHT sk_test_!
STRIPE_PUBLISHABLE_KEY="pk_live_..." # Frontend

# ✅ 3. Live Webhook konfigurieren
URL: https://your-production-domain.com/
Events: checkout.session.completed, invoice.payment_succeeded  
Secret: whsec_... (Live secret - neu generieren!)

# ✅ 4. Live Price IDs aus Stripe Dashboard
STRIPE_PRICE_SMALL_ID="price_1ABC..."  # 100 Credits
STRIPE_PRICE_MEDIUM_ID="price_1DEF..." # 500 Credits  
STRIPE_PRICE_LARGE_ID="price_1GHI..." # 1500 Credits
```

### 🔐 SECURITY CHECKLIST

```bash
# ✅ Alle Secrets neu generieren für Production
NEXTAUTH_SECRET="[64-chars-random]"
SESSION_SECRET_KEY="[64-chars-random]"
DATABASE_URL="postgresql://prod-user:prod-pass@prod-host:5432/prod_db"

# ✅ Production URLs setzen
NEXTAUTH_URL="https://your-domain.com"
ALLOWED_ORIGINS='["https://your-domain.com"]'

# ❌ Debug-Modi ausschalten
DEBUG="false"
E2E_TEST_MODE=""
LOG_LEVEL="info"
```

### 🗄️ DATABASE MIGRATION

```bash
# ✅ 1. Backup Development
pg_dump $DEV_DATABASE_URL > backup_dev.sql

# ✅ 2. Production Setup
# Render: PostgreSQL Addon oder externe DB
# Connection String: postgresql://...

# ✅ 3. Migration ausführen
cd apps/backend
uv run alembic upgrade head
```

### 🚀 DEPLOYMENT REIHENFOLGE

```bash
# 1. ✅ Backend zuerst (Render)
git push origin main  # Trigger auto-deploy

# 2. ✅ Webhook URL in Stripe aktualisieren
# Alt: https://resume-matcher-backend-j06k.onrender.com/
# Neu: https://your-production-backend.onrender.com/

# 3. ✅ Frontend deployment (Vercel)  
vercel --prod

# 4. ✅ DNS und SSL konfigurieren
# Domain pointing, SSL certificates
```

### 🧪 LIVE TESTING PROTOKOLL

```bash
# ⚠️ VORSICHT: Echte Zahlungen!

# Test Sequence:
1. Kleiner Kauf (1-5€) 
2. Credit balance prüfen
3. Webhook logs überprüfen
4. Database entries validieren

# Emergency Contact:
# Stripe: Dashboard -> Support
# Render: Dashboard -> Support ticket
```

### 📊 MONITORING ESSENTIALS

```bash
# Health Endpoints überwachen:
GET /healthz -> 200 OK
POST / -> Stripe webhooks (400/200 normal)

# Key Metrics:
- Payment Success Rate: >95%
- API Response Time: <2s
- Error Rate: <1%
- Webhook Delivery: >99%

# Render Logs prüfen:
- "Successfully imported app.main" ✅
- "Database connection established" ✅  
- "Stripe webhook received" ✅
- "Credits added successfully" ✅
```

### 🆘 EMERGENCY ROLLBACK

```bash
# Render: Previous deployment
Dashboard -> Deployments -> "Revert to this deploy"

# Vercel: Git rollback
git revert [commit-hash]
vercel --prod

# Stripe: Webhook URL zurücksetzen
Dashboard -> Webhooks -> Edit endpoint URL
```

### 📞 PRODUCTION SUPPORT

```bash
# Level 1: Check status dashboards
- Render service status
- Vercel deployment status  
- Stripe webhook deliveries

# Level 2: Check logs
- Render application logs
- Stripe webhook attempts
- Database connection logs

# Level 3: Verify configuration
- Environment variables
- Webhook signatures
- Database migrations
```

---

**🎯 READY FOR PRODUCTION!**

Mit dieser Checklist ist das System production-ready! 

**Wichtigste Punkte:**
1. **Stripe Live Keys** und **Webhook URL** aktualisieren
2. **Alle Secrets** für Production neu generieren  
3. **Database** migrieren und testen
4. **Monitoring** aktivieren und alerts setzen

**Die Credits funktionieren dann live! 💰**
