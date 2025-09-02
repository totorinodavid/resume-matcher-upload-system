# 🎯 QUICK START: Next.js Credit System

## Sofort starten ohne alte Daten

**Perfekt für Clean Setup!** 🚀

---

## ⚡ 5-Minuten Setup

```bash
# 1. Projekt erstellen
npx create-next-app@latest resume-matcher-nextjs --typescript --tailwind --app
cd resume-matcher-nextjs

# 2. Dependencies
npm install @prisma/client prisma stripe @auth0/nextjs-auth0
npm install -D @types/node tsx

# 3. Prisma Setup
npx prisma init

# 4. Schema kopieren (aus clean_prisma_schema.prisma)
# 5. Migrate
npx prisma migrate dev --name init
npx prisma generate

# 6. Seed Database (optional)
npx tsx scripts/seed.ts

# 7. Development
npm run dev
```

---

## 📁 Dateien bereit

### **NEXTJS_CLEAN_SETUP.md**
- Komplette Setup-Anleitung
- Keine Migration nötig
- Credit-Preise und Flow

### **clean_prisma_schema.prisma** 
- Sauberes Schema ohne Legacy-Felder
- Ready für Resume + Job Analysis
- Stripe Integration vorbereitet

### **seed_clean_database.ts**
- Erstellt Standard-Preise (€5/€20/€35)
- Demo User mit 50 Welcome Credits
- Credit-Kosten Referenz

### **STRIPE_CREDIT_SYSTEM_VOLLSTAENDIG.txt** (bereits vorhanden)
- Komplette Next.js Implementation
- API Routes + Webhooks
- Dashboard Components

---

## 🎯 Credits System

### Preise:
- **Starter**: €5.00 → 100 Credits
- **Pro**: €20.00 → 500 Credits 🔥
- **Premium**: €35.00 → 1000 Credits (30% OFF)

### Kosten pro Aktion:
- Resume Analysis: **10 Credits**
- Job Matching: **5 Credits** 
- Skill Extraction: **3 Credits**
- ATS Optimization: **8 Credits**
- Cover Letter: **12 Credits**

### Welcome Bonus:
- Neue User: **50 Free Credits** 🎁

---

## ✅ Vorteile Clean Setup

- 🚀 **Sofort produktiv** - Kein Migration-Overhead
- 🧹 **Moderne Architektur** - Next.js 14 + Prisma
- 🔒 **Security First** - Auth0 Integration
- 📱 **Mobile Ready** - Responsive Components
- ⚡ **Performance** - App Router + Server Actions
- 💳 **Stripe Ready** - Production-ready Payments

**Kannst sofort loslegen! Der komplette Code ist in STRIPE_CREDIT_SYSTEM_VOLLSTAENDIG.txt** 🎉
