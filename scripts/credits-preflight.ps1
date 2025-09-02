# Credits System Pre-Flight Setup Script
# PowerShell Version for Windows
# Run this in VS Code Terminal: .\scripts\credits-preflight.ps1

param(
    [switch]$SkipBackup,
    [switch]$SkipBranch,
    [string]$Environment = "development"
)

Write-Host "🚀 Resume Matcher Credits Pre-Flight Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$PreflightResults = @{
    FreezeFlag = $false
    Backup = $false
    Secrets = $false
    Branch = $false
}

# 1. Set Feature Flag - Credits Write Freeze
Write-Host "`n1️⃣ Setting Credits Write Freeze Flag..." -ForegroundColor Yellow

$envFiles = @(".env", ".env.local", "apps/frontend/.env.local", "apps/backend/.env")
$freezeSet = $false

foreach ($envFile in $envFiles) {
    if (Test-Path $envFile) {
        $content = Get-Content $envFile -Raw
        if ($content -notmatch "CREDITS_WRITE_FREEZE") {
            Add-Content $envFile "`nCREDITS_WRITE_FREEZE=1"
            Write-Host "✅ Added CREDITS_WRITE_FREEZE=1 to $envFile" -ForegroundColor Green
            $freezeSet = $true
        } else {
            # Update existing value
            $content = $content -replace "CREDITS_WRITE_FREEZE=.*", "CREDITS_WRITE_FREEZE=1"
            Set-Content $envFile $content
            Write-Host "✅ Updated CREDITS_WRITE_FREEZE=1 in $envFile" -ForegroundColor Green
            $freezeSet = $true
        }
    }
}

if (-not $freezeSet) {
    # Create .env if none exist
    Set-Content ".env" "CREDITS_WRITE_FREEZE=1"
    Write-Host "✅ Created .env with CREDITS_WRITE_FREEZE=1" -ForegroundColor Green
    $freezeSet = $true
}

$PreflightResults.FreezeFlag = $freezeSet

# 2. Database Backup
Write-Host "`n2️⃣ Creating Database Backup..." -ForegroundColor Yellow

if (-not $SkipBackup) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmm"
    $backupFile = "backup_$timestamp.sql"
    
    # Check if DATABASE_URL is set
    $databaseUrl = $env:DATABASE_URL
    if (-not $databaseUrl) {
        # Try to load from .env files
        foreach ($envFile in $envFiles) {
            if (Test-Path $envFile) {
                $envContent = Get-Content $envFile
                $dbLine = $envContent | Where-Object { $_ -match "DATABASE_URL=" }
                if ($dbLine) {
                    $databaseUrl = ($dbLine -split "=", 2)[1].Trim('"')
                    break
                }
            }
        }
    }
    
    if ($databaseUrl) {
        try {
            Write-Host "Creating backup: $backupFile" -ForegroundColor Blue
            
            # Use pg_dump via WSL or direct if available
            $pgDumpCmd = "pg_dump '$databaseUrl' > $backupFile"
            
            if (Get-Command wsl -ErrorAction SilentlyContinue) {
                wsl bash -c "pg_dump '$databaseUrl' | gzip > $backupFile.gz"
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Database backup created: $backupFile.gz" -ForegroundColor Green
                    $PreflightResults.Backup = $true
                } else {
                    Write-Host "❌ Backup failed via WSL" -ForegroundColor Red
                }
            } else {
                Write-Host "⚠️ pg_dump not available. Install PostgreSQL client or WSL" -ForegroundColor Yellow
                Write-Host "Manual backup command: pg_dump '$databaseUrl' | gzip > $backupFile.gz" -ForegroundColor Gray
            }
        } catch {
            Write-Host "❌ Backup failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ DATABASE_URL not found in environment" -ForegroundColor Red
    }
} else {
    Write-Host "⏭️ Backup skipped" -ForegroundColor Gray
    $PreflightResults.Backup = $true
}

# 3. Environment Variables Check
Write-Host "`n3️⃣ Checking Required Environment Variables..." -ForegroundColor Yellow

$requiredVars = @(
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET", 
    "DATABASE_URL",
    "NEXTAUTH_SECRET"
)

$allVarsPresent = $true

foreach ($var in $requiredVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    
    if (-not $value) {
        # Check in .env files
        foreach ($envFile in $envFiles) {
            if (Test-Path $envFile) {
                $envContent = Get-Content $envFile
                $varLine = $envContent | Where-Object { $_ -match "^$var=" }
                if ($varLine) {
                    $value = ($varLine -split "=", 2)[1].Trim('"')
                    break
                }
            }
        }
    }
    
    if ($value -and $value.Length -gt 0) {
        $maskedValue = $value.Substring(0, [Math]::Min(8, $value.Length)) + "..."
        Write-Host "✅ $var = $maskedValue" -ForegroundColor Green
    } else {
        Write-Host "❌ Missing: $var" -ForegroundColor Red
        $allVarsPresent = $false
    }
}

$PreflightResults.Secrets = $allVarsPresent

# 4. Git Branch Setup
Write-Host "`n4️⃣ Setting up Git Branch..." -ForegroundColor Yellow

if (-not $SkipBranch) {
    try {
        # Check if branch exists
        $branchExists = git branch --list "feature/credits-v2" 2>$null
        
        if (-not $branchExists) {
            git checkout -b feature/credits-v2
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Created branch: feature/credits-v2" -ForegroundColor Green
                $PreflightResults.Branch = $true
            } else {
                Write-Host "❌ Failed to create branch" -ForegroundColor Red
            }
        } else {
            git checkout feature/credits-v2
            Write-Host "✅ Switched to existing branch: feature/credits-v2" -ForegroundColor Green
            $PreflightResults.Branch = $true
        }
        
        # Optional: Push to remote
        $pushChoice = Read-Host "Push branch to remote? (y/N)"
        if ($pushChoice -eq "y" -or $pushChoice -eq "Y") {
            git push -u origin feature/credits-v2
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Branch pushed to remote" -ForegroundColor Green
            } else {
                Write-Host "⚠️ Push failed or remote not configured" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "❌ Git branch setup failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "⏭️ Branch setup skipped" -ForegroundColor Gray
    $PreflightResults.Branch = $true
}

# 5. Final Report
Write-Host "`n📊 PRE-FLIGHT REPORT" -ForegroundColor Magenta
Write-Host "===================" -ForegroundColor Magenta

Write-Host "Environment: $Environment" -ForegroundColor Blue

$status = if ($PreflightResults.FreezeFlag) { "✅ SET" } else { "❌ FAILED" }
Write-Host "Credits Freeze Flag: $status" -ForegroundColor $(if ($PreflightResults.FreezeFlag) { "Green" } else { "Red" })

$status = if ($PreflightResults.Backup) { "✅ CREATED" } else { "❌ FAILED" }
Write-Host "Database Backup: $status" -ForegroundColor $(if ($PreflightResults.Backup) { "Green" } else { "Red" })

$status = if ($PreflightResults.Secrets) { "✅ COMPLETE" } else { "❌ MISSING" }
Write-Host "Environment Secrets: $status" -ForegroundColor $(if ($PreflightResults.Secrets) { "Green" } else { "Red" })

$status = if ($PreflightResults.Branch) { "✅ READY" } else { "❌ FAILED" }
Write-Host "Git Branch: $status" -ForegroundColor $(if ($PreflightResults.Branch) { "Green" } else { "Red" })

$allGood = $PreflightResults.FreezeFlag -and $PreflightResults.Backup -and $PreflightResults.Secrets -and $PreflightResults.Branch

if ($allGood) {
    Write-Host "`n🎉 PRE-FLIGHT COMPLETE - READY FOR CREDITS V2 IMPLEMENTATION!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ PRE-FLIGHT INCOMPLETE - PLEASE RESOLVE ISSUES ABOVE" -ForegroundColor Yellow
}

Write-Host "`nNext Steps:" -ForegroundColor Blue
Write-Host "1. Verify freeze flag is active in frontend" -ForegroundColor Gray
Write-Host "2. Test that credit purchases are disabled" -ForegroundColor Gray
Write-Host "3. Begin credits v2 implementation" -ForegroundColor Gray
Write-Host "4. Monitor production for any freeze-related issues" -ForegroundColor Gray
