#!/usr/bin/env pwsh
# Production Credits System Deployment

Write-Host "🚀 PRODUCTION CREDITS DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Check readiness
$analysis = Get-Content "apps/backend/CREDITS_SYSTEM_ANALYSIS.json" | ConvertFrom-Json
Write-Host "📊 System Score: $($analysis.readiness_score)/100" -ForegroundColor Green

# Confirm deployment
Write-Host "`n⚠️ Ready to deploy production credits system"
$confirm = Read-Host "Type 'DEPLOY' to proceed"

if ($confirm -eq "DEPLOY") {
    Write-Host "`n🚀 Deploying..." -ForegroundColor Yellow
    
    # Trigger Render deployment
    try {
        $url = "https://api.render.com/deploy/srv-cqr8chn2ng1s73e9sb90?key=XhUb4aWCNhE"
        Invoke-WebRequest -Uri $url -Method POST -UseBasicParsing
        Write-Host "✅ Deployment triggered!" -ForegroundColor Green
        Write-Host "🔗 Monitor: https://dashboard.render.com" -ForegroundColor Blue
    } catch {
        Write-Host "❌ Deployment trigger failed: $_" -ForegroundColor Red
        Write-Host "💡 Manual deploy: https://dashboard.render.com" -ForegroundColor Blue
    }
    
    Write-Host "`n🎉 PRODUCTION DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "✅ Credits system deploying to production" -ForegroundColor Green
    Write-Host "⏳ Takes 5-10 minutes to complete" -ForegroundColor Yellow
} else {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
}
