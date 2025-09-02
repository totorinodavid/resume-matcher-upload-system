#!/usr/bin/env pwsh
# Deploy Credit System to gojob.ing Production
# Autor: Resume Matcher Team
# Datum: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Write-Host "🚀 DEPLOYING CREDIT SYSTEM TO gojob.ing PRODUCTION" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# 1. Datenbank Migration checken
Write-Host "📊 Checking database migration status..." -ForegroundColor Yellow
Set-Location apps/frontend
npx prisma migrate status --schema prisma/schema.prisma
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Database needs migration!" -ForegroundColor Red
    Write-Host "Running database migration..." -ForegroundColor Yellow
    npx prisma migrate deploy --schema prisma/schema.prisma
}

# 2. Prisma Client generieren
Write-Host "🔧 Generating Prisma client..." -ForegroundColor Yellow
npx prisma generate --schema prisma/schema.prisma

# 3. TypeScript Build
Write-Host "🏗️ Building TypeScript..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# 4. Git commit und push
Write-Host "📤 Committing and pushing to production..." -ForegroundColor Yellow
git add .
git commit -m "🚀 Deploy Credit System to gojob.ing - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push origin security-hardening-neon

Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "🌐 Credit System live at: https://gojob.ing/billing" -ForegroundColor Cyan
Write-Host "💳 Stripe Dashboard: https://dashboard.stripe.com/test/payments" -ForegroundColor Cyan
Write-Host "📊 Database: Render PostgreSQL" -ForegroundColor Cyan

# 5. Webhook URL für Stripe konfigurieren
Write-Host "" -ForegroundColor Yellow
Write-Host "⚠️  WICHTIG: Stripe Webhook URL konfigurieren:" -ForegroundColor Yellow
Write-Host "   URL: https://gojob.ing/api/stripe/credits-webhook" -ForegroundColor White
Write-Host "   Events: checkout.session.completed, payment_intent.succeeded" -ForegroundColor White

# 6. Production Test
Write-Host "" -ForegroundColor Yellow
Write-Host "🧪 Ready for production testing!" -ForegroundColor Green
Write-Host "   1. Gehe zu https://gojob.ing" -ForegroundColor White
Write-Host "   2. Login mit Google" -ForegroundColor White
Write-Host "   3. Besuche /billing für Credit-Kauf" -ForegroundColor White
Write-Host "   4. Teste Stripe Checkout Flow" -ForegroundColor White
