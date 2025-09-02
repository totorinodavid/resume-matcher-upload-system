# Credits System Pre-Flight Setup Script
# PowerShell Version for Windows

param(
    [switch]$SkipBackup,
    [switch]$SkipBranch
)

Write-Host "Credits Pre-Flight Setup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# 1. Set Credits Freeze Flag
Write-Host "`n1. Setting Credits Write Freeze Flag..." -ForegroundColor Yellow

$envFiles = @(".env", "apps/frontend/.env.local", "apps/backend/.env")
$freezeSet = $false

foreach ($envFile in $envFiles) {
    if (Test-Path $envFile) {
        $content = Get-Content $envFile -Raw
        if ($content -notmatch "CREDITS_WRITE_FREEZE") {
            Add-Content $envFile "`nCREDITS_WRITE_FREEZE=1"
            Write-Host "Added CREDITS_WRITE_FREEZE=1 to $envFile" -ForegroundColor Green
            $freezeSet = $true
        }
    }
}

if (-not $freezeSet) {
    Set-Content ".env" "CREDITS_WRITE_FREEZE=1"
    Write-Host "Created .env with CREDITS_WRITE_FREEZE=1" -ForegroundColor Green
}

# 2. Check Environment Variables
Write-Host "`n2. Checking Environment Variables..." -ForegroundColor Yellow

$requiredVars = @("STRIPE_SECRET_KEY", "DATABASE_URL", "NEXTAUTH_SECRET")
$allPresent = $true

foreach ($var in $requiredVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if (-not $value) {
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
        $masked = $value.Substring(0, [Math]::Min(8, $value.Length)) + "..."
        Write-Host "$var = $masked" -ForegroundColor Green
    } else {
        Write-Host "Missing: $var" -ForegroundColor Red
        $allPresent = $false
    }
}

# 3. Git Branch
if (-not $SkipBranch) {
    Write-Host "`n3. Setting up Git Branch..." -ForegroundColor Yellow
    try {
        git checkout -b feature/credits-v2 2>$null
        Write-Host "Created branch: feature/credits-v2" -ForegroundColor Green
    } catch {
        git checkout feature/credits-v2 2>$null
        Write-Host "Switched to branch: feature/credits-v2" -ForegroundColor Green
    }
}

Write-Host "`nPre-flight setup complete!" -ForegroundColor Green
Write-Host "Next: Test environment checker with: node scripts\env-checker.js" -ForegroundColor Blue
