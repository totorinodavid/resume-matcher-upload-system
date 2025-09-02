# Credits System Pre-Flight Setup

This directory contains scripts for preparing the Resume Matcher system before implementing Credits V2.

## Scripts Overview

### 1. PowerShell Script (Windows)
**File:** `credits-preflight.ps1`
**Usage:** 
```powershell
.\scripts\credits-preflight.ps1
.\scripts\credits-preflight.ps1 -SkipBackup
.\scripts\credits-preflight.ps1 -Environment "production"
```

### 2. Bash Script (Unix/Linux/macOS)
**File:** `credits-preflight.sh`  
**Usage:**
```bash
chmod +x scripts/credits-preflight.sh
./scripts/credits-preflight.sh
./scripts/credits-preflight.sh --skip-backup --environment=production
```

### 3. Environment Checker (Node.js)
**File:** `env-checker.js`
**Usage:**
```bash
node scripts/env-checker.js
```

### 4. Database Backup (Python)
**File:** `db-backup.py`
**Usage:**
```bash
python scripts/db-backup.py
python scripts/db-backup.py --compress --output-dir=backups
python scripts/db-backup.py --list
python scripts/db-backup.py --cleanup 5
```

## What These Scripts Do

### 🔒 1. Credits Write Freeze
- Sets `CREDITS_WRITE_FREEZE=1` in all `.env` files
- Prevents new credit purchases during migration
- Safe fallback for production

### 📀 2. Database Backup
- Creates timestamped PostgreSQL dumps
- Supports compression with gzip
- Automatic cleanup of old backups
- Compatible with Render Postgres

### 🔑 3. Environment Validation
- Checks all required environment variables
- Validates secret key formats
- Masks sensitive values in output
- Color-coded status reporting

### 🌿 4. Git Branch Management
- Creates `feature/credits-v2` branch
- Optional push to remote
- Safe branch switching

## Quick Start

### Windows (PowerShell)
```powershell
# Run complete pre-flight check
.\scripts\credits-preflight.ps1

# Check environment variables only
node scripts\env-checker.js

# Create database backup only
python scripts\db-backup.py
```

### Unix/Linux/macOS
```bash
# Make scripts executable
chmod +x scripts/credits-preflight.sh

# Run complete pre-flight check
./scripts/credits-preflight.sh

# Check environment variables only
node scripts/env-checker.js

# Create database backup only
python scripts/db-backup.py
```

## Environment Variables Required

The scripts check for these essential variables:

- `STRIPE_SECRET_KEY` - Stripe payment processing
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook verification
- `DATABASE_URL` - PostgreSQL connection string
- `NEXTAUTH_SECRET` - Session encryption key
- `OPENAI_API_KEY` - AI processing (optional)
- `CREDITS_WRITE_FREEZE` - System freeze flag

## Dependencies

### System Requirements
- **PostgreSQL Client**: `pg_dump` for database backups
- **Node.js**: For environment checking
- **Python 3.7+**: For database utilities
- **Git**: For branch management

### Install Dependencies

**Windows:**
```powershell
# Install PostgreSQL client
winget install PostgreSQL.PostgreSQL

# Install Node.js
winget install OpenJS.NodeJS

# Install Python
winget install Python.Python.3
```

**macOS:**
```bash
# Install PostgreSQL client
brew install postgresql

# Install Node.js
brew install node

# Install Python
brew install python
```

**Ubuntu/Debian:**
```bash
# Install PostgreSQL client
sudo apt-get install postgresql-client

# Install Node.js
sudo apt-get install nodejs npm

# Install Python
sudo apt-get install python3 python3-pip
```

## Output Examples

### ✅ Successful Pre-Flight
```
🚀 Resume Matcher Credits Pre-Flight Setup
=========================================

1️⃣ Setting Credits Write Freeze Flag...
✅ Added CREDITS_WRITE_FREEZE=1 to .env

2️⃣ Creating Database Backup...
✅ Database backup created: backup_20250902_1430.sql.gz

3️⃣ Checking Required Environment Variables...
✅ STRIPE_SECRET_KEY = sk_test_...
✅ STRIPE_WEBHOOK_SECRET = whsec_...
✅ DATABASE_URL = postgres://***:***@...
✅ NEXTAUTH_SECRET = abc12345...

4️⃣ Setting up Git Branch...
✅ Created branch: feature/credits-v2

📊 PRE-FLIGHT REPORT
===================
Environment: development
Credits Freeze Flag: ✅ SET
Database Backup: ✅ CREATED
Environment Secrets: ✅ COMPLETE
Git Branch: ✅ READY

🎉 PRE-FLIGHT COMPLETE - READY FOR CREDITS V2 IMPLEMENTATION!
```

### ❌ Issues Found
```
📊 PRE-FLIGHT REPORT
===================
Credits Freeze Flag: ✅ SET
Database Backup: ❌ FAILED
Environment Secrets: ❌ MISSING
Git Branch: ✅ READY

⚠️ PRE-FLIGHT INCOMPLETE - PLEASE RESOLVE ISSUES ABOVE
```

## Troubleshooting

### Database Backup Issues
- **pg_dump not found**: Install PostgreSQL client tools
- **Connection failed**: Check DATABASE_URL format
- **Permission denied**: Verify database credentials

### Environment Variable Issues
- **Variables not found**: Check `.env` file locations
- **Invalid format**: Verify secret key patterns
- **Missing secrets**: Add required variables to `.env`

### Git Branch Issues
- **Branch creation failed**: Check git repository status
- **Push failed**: Verify remote repository access
- **Permission denied**: Check git credentials

## Security Notes

- Scripts mask sensitive values in output
- Backup files contain full database content - secure appropriately
- Environment variables are never logged in plain text
- Temporary files are cleaned up automatically

## Next Steps After Pre-Flight

1. **Verify Freeze Flag**: Test that credit purchases are disabled in frontend
2. **Monitor Production**: Watch for any freeze-related issues
3. **Begin Implementation**: Start building Credits V2 system
4. **Rollback Plan**: Keep backup files safe for potential rollback

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review script output for specific error messages
3. Verify all dependencies are installed
4. Check environment variable configuration
