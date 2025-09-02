# 🚀 NEXT.JS CREDIT SYSTEM - CLEAN SETUP

## Neues System ohne Migration

**Ziel**: Frisches Next.js Credit-System ohne alte Daten zu übernehmen

---

## 🎯 Setup-Strategie

### Vorteile des Clean Setup:
- ✅ **Keine Daten-Migration nötig** 
- ✅ **Saubere Prisma-Datenbank**
- ✅ **Moderne Architektur von Anfang an**
- ✅ **Keine Legacy-Kompatibilität**
- ✅ **Einfacher zu testen**

### Was passiert mit dem alten System:
- Python/FastAPI System läuft parallel weiter
- Neue User verwenden Next.js System
- Alter Credit-Saldo wird nicht übertragen
- Clean Cut zwischen alt und neu

---

## 🛠️ Next.js Setup (Clean)

### 1. Projekt erstellen
```bash
npx create-next-app@latest resume-matcher-nextjs --typescript --tailwind --app
cd resume-matcher-nextjs
```

### 2. Dependencies installieren
```bash
npm install @prisma/client prisma stripe @auth0/nextjs-auth0
npm install -D @types/node tsx
```

### 3. Prisma Setup (Clean Schema)
```bash
npx prisma init
```

### 4. Environment Setup
```env
# .env.local
DATABASE_URL="postgresql://user:pass@localhost:5432/resume_matcher_nextjs"
STRIPE_SECRET_KEY="sk_test_..."
STRIPE_PUBLISHABLE_KEY="pk_test_..."
STRIPE_WEBHOOK_SECRET="whsec_..."
NEXT_PUBLIC_BASE_URL="http://localhost:3000"
AUTH0_SECRET="..."
AUTH0_BASE_URL="http://localhost:3000"
AUTH0_ISSUER_BASE_URL="https://your-tenant.auth0.com"
AUTH0_CLIENT_ID="..."
AUTH0_CLIENT_SECRET="..."
```

---

## 📊 Clean Prisma Schema

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id               String             @id @default(cuid())
  email            String             @unique
  name             String?
  credits          Int                @default(0)
  
  // Stripe integration
  stripeCustomerId String?            @unique
  
  createdAt        DateTime           @default(now())
  updatedAt        DateTime           @updatedAt
  
  transactions     CreditTransaction[]

  @@map("users")
}

model CreditTransaction {
  id            String   @id @default(cuid())
  userId        String
  delta         Int      // +100 for purchase, -10 for resume analysis
  reason        String   // "purchase", "resume_analysis", "job_match"
  stripeEventId String?  @unique
  
  metadata      Json?    // Flexible storage
  createdAt     DateTime @default(now())
  
  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("credit_transactions")
}

model Price {
  id             String   @id @default(cuid())
  stripePriceId  String   @unique
  creditsPerUnit Int      // 100 credits
  priceInCents   Int      // 500 = €5.00
  currency       String   @default("eur")
  active         Boolean  @default(true)
  
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  @@map("prices")
}
```

---

## 🎨 Initial Data Setup

### Erstelle Standard-Preise
```typescript
// scripts/seed.ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function seedPrices() {
  console.log('🌱 Seeding prices...')
  
  await prisma.price.createMany({
    data: [
      {
        stripePriceId: 'price_1234567890',  // Aus Stripe Dashboard
        creditsPerUnit: 100,
        priceInCents: 500,  // €5.00
        currency: 'eur',
        active: true,
      },
      {
        stripePriceId: 'price_0987654321',  // Aus Stripe Dashboard  
        creditsPerUnit: 500,
        priceInCents: 2000,  // €20.00
        currency: 'eur',
        active: true,
      },
      {
        stripePriceId: 'price_1111111111',  // Aus Stripe Dashboard
        creditsPerUnit: 1000,
        priceInCents: 3500,  // €35.00 (30% discount)
        currency: 'eur', 
        active: true,
      }
    ],
    skipDuplicates: true,
  })
  
  console.log('✅ Prices seeded')
}

seedPrices()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e)
    prisma.$disconnect()
    process.exit(1)
  })
```

---

## 🚀 Implementierung (aus STRIPE_CREDIT_SYSTEM_VOLLSTAENDIG.txt)

### API Routes:
- `app/api/checkout/route.ts` - Stripe Checkout
- `app/api/stripe/webhook/route.ts` - Webhook Handler
- `app/api/credits/route.ts` - Credit Balance

### Server Actions:
- `lib/actions/credits.ts` - Credit Management
- `lib/actions/checkout.ts` - Purchase Logic

### Components:
- `components/CreditPurchase.tsx` - Kaufen Interface
- `components/CreditBalance.tsx` - Balance anzeigen
- `components/CreditHistory.tsx` - Transaction History

### Pages:
- `app/credits/page.tsx` - Credit Dashboard
- `app/checkout/page.tsx` - Purchase Page

---

## ⚡ Quick Start Commands

```bash
# 1. Setup
npx create-next-app@latest resume-matcher-nextjs --typescript --tailwind --app
cd resume-matcher-nextjs

# 2. Install
npm install @prisma/client prisma stripe @auth0/nextjs-auth0
npm install -D @types/node tsx

# 3. Prisma
npx prisma init
# (Schema aus diesem Guide kopieren)
npx prisma migrate dev --name init
npx prisma generate

# 4. Seed
npx tsx scripts/seed.ts

# 5. Development
npm run dev
```

---

## 🎯 Startup Flow

### Neue User Experience:
1. **Registrierung** → 0 Credits
2. **Welcome Bonus** → +50 Credits (optional)
3. **Ersten Purchase** → Stripe Checkout
4. **Resume Analysis** → -10 Credits pro Analyse
5. **Job Matching** → -5 Credits pro Match

### Credit Pricing:
- **Starter**: €5.00 → 100 Credits
- **Pro**: €20.00 → 500 Credits  
- **Premium**: €35.00 → 1000 Credits (Best Value)

---

## ✅ Advantages Clean Setup

- 🚀 **Schneller Start** - Keine Migration-Komplexität
- 🧹 **Saubere Architektur** - Moderne Patterns von Anfang an
- 🔒 **Bessere Security** - Neue Auth0 Integration
- 📱 **Mobile-First** - Responsive Design
- ⚡ **Performance** - Next.js 14 App Router
- 🎨 **UI/UX** - Tailwind + Radix UI Components

**Ready to build! 🎉**
