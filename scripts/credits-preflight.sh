#!/bin/bash
# Credits System Pre-Flight Setup Script
# Unix/Linux/macOS Version
# Usage: ./scripts/credits-preflight.sh [--skip-backup] [--skip-branch] [--environment=production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
SKIP_BACKUP=false
SKIP_BRANCH=false
ENVIRONMENT="development"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backup)
            SKIP_BACKUP=true
            shift
            ;;
        --skip-branch)
            SKIP_BRANCH=true
            shift
            ;;
        --environment=*)
            ENVIRONMENT="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--skip-backup] [--skip-branch] [--environment=ENV]"
            echo "Options:"
            echo "  --skip-backup     Skip database backup creation"
            echo "  --skip-branch     Skip git branch setup"
            echo "  --environment=ENV Set environment (default: development)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Results tracking
declare -A PREFLIGHT_RESULTS
PREFLIGHT_RESULTS[freeze_flag]=false
PREFLIGHT_RESULTS[backup]=false
PREFLIGHT_RESULTS[secrets]=false
PREFLIGHT_RESULTS[branch]=false

echo -e "${CYAN}🚀 Resume Matcher Credits Pre-Flight Setup${NC}"
echo -e "${CYAN}=========================================${NC}"

# 1. Set Feature Flag - Credits Write Freeze
echo -e "\n${YELLOW}1️⃣ Setting Credits Write Freeze Flag...${NC}"

ENV_FILES=(".env" ".env.local" "apps/frontend/.env.local" "apps/backend/.env")
FREEZE_SET=false

for env_file in "${ENV_FILES[@]}"; do
    if [[ -f "$env_file" ]]; then
        if grep -q "CREDITS_WRITE_FREEZE" "$env_file"; then
            # Update existing value
            sed -i.bak 's/CREDITS_WRITE_FREEZE=.*/CREDITS_WRITE_FREEZE=1/' "$env_file"
            echo -e "${GREEN}✅ Updated CREDITS_WRITE_FREEZE=1 in $env_file${NC}"
            FREEZE_SET=true
        else
            # Add new value
            echo "CREDITS_WRITE_FREEZE=1" >> "$env_file"
            echo -e "${GREEN}✅ Added CREDITS_WRITE_FREEZE=1 to $env_file${NC}"
            FREEZE_SET=true
        fi
    fi
done

if [[ "$FREEZE_SET" == false ]]; then
    # Create .env if none exist
    echo "CREDITS_WRITE_FREEZE=1" > .env
    echo -e "${GREEN}✅ Created .env with CREDITS_WRITE_FREEZE=1${NC}"
    FREEZE_SET=true
fi

PREFLIGHT_RESULTS[freeze_flag]=$FREEZE_SET

# 2. Database Backup
echo -e "\n${YELLOW}2️⃣ Creating Database Backup...${NC}"

if [[ "$SKIP_BACKUP" == false ]]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="backup_${TIMESTAMP}.sql.gz"
    
    # Check if DATABASE_URL is set
    DATABASE_URL="${DATABASE_URL:-}"
    
    if [[ -z "$DATABASE_URL" ]]; then
        # Try to load from .env files
        for env_file in "${ENV_FILES[@]}"; do
            if [[ -f "$env_file" ]]; then
                DATABASE_URL=$(grep "^DATABASE_URL=" "$env_file" | cut -d'=' -f2- | tr -d '"')
                if [[ -n "$DATABASE_URL" ]]; then
                    break
                fi
            fi
        done
    fi
    
    if [[ -n "$DATABASE_URL" ]]; then
        if command -v pg_dump &> /dev/null; then
            echo -e "${BLUE}Creating backup: $BACKUP_FILE${NC}"
            
            if pg_dump "$DATABASE_URL" | gzip > "$BACKUP_FILE"; then
                echo -e "${GREEN}✅ Database backup created: $BACKUP_FILE${NC}"
                
                # Verify backup
                if gzip -t "$BACKUP_FILE" 2>/dev/null; then
                    echo -e "${GREEN}✅ Backup file verified${NC}"
                    PREFLIGHT_RESULTS[backup]=true
                else
                    echo -e "${RED}❌ Backup file corrupted${NC}"
                fi
            else
                echo -e "${RED}❌ Backup failed${NC}"
            fi
        else
            echo -e "${YELLOW}⚠️ pg_dump not available. Install PostgreSQL client${NC}"
            echo -e "${YELLOW}Manual backup command: pg_dump '$DATABASE_URL' | gzip > $BACKUP_FILE${NC}"
        fi
    else
        echo -e "${RED}❌ DATABASE_URL not found in environment${NC}"
    fi
else
    echo -e "${BLUE}⏭️ Backup skipped${NC}"
    PREFLIGHT_RESULTS[backup]=true
fi

# 3. Environment Variables Check
echo -e "\n${YELLOW}3️⃣ Checking Required Environment Variables...${NC}"

REQUIRED_VARS=(
    "STRIPE_SECRET_KEY"
    "STRIPE_WEBHOOK_SECRET"
    "DATABASE_URL"
    "NEXTAUTH_SECRET"
)

ALL_VARS_PRESENT=true

for var in "${REQUIRED_VARS[@]}"; do
    # Check environment variable
    value="${!var:-}"
    
    if [[ -z "$value" ]]; then
        # Check in .env files
        for env_file in "${ENV_FILES[@]}"; do
            if [[ -f "$env_file" ]]; then
                value=$(grep "^${var}=" "$env_file" | cut -d'=' -f2- | tr -d '"')
                if [[ -n "$value" ]]; then
                    break
                fi
            fi
        done
    fi
    
    if [[ -n "$value" ]]; then
        masked_value="${value:0:8}..."
        echo -e "${GREEN}✅ $var = $masked_value${NC}"
    else
        echo -e "${RED}❌ Missing: $var${NC}"
        ALL_VARS_PRESENT=false
    fi
done

PREFLIGHT_RESULTS[secrets]=$ALL_VARS_PRESENT

# 4. Git Branch Setup
echo -e "\n${YELLOW}4️⃣ Setting up Git Branch...${NC}"

if [[ "$SKIP_BRANCH" == false ]]; then
    if command -v git &> /dev/null; then
        # Check if branch exists
        if git show-ref --verify --quiet refs/heads/feature/credits-v2; then
            git checkout feature/credits-v2
            echo -e "${GREEN}✅ Switched to existing branch: feature/credits-v2${NC}"
            PREFLIGHT_RESULTS[branch]=true
        else
            if git checkout -b feature/credits-v2; then
                echo -e "${GREEN}✅ Created branch: feature/credits-v2${NC}"
                PREFLIGHT_RESULTS[branch]=true
            else
                echo -e "${RED}❌ Failed to create branch${NC}"
            fi
        fi
        
        # Optional: Push to remote
        echo -n "Push branch to remote? (y/N): "
        read -r push_choice
        if [[ "$push_choice" =~ ^[Yy]$ ]]; then
            if git push -u origin feature/credits-v2; then
                echo -e "${GREEN}✅ Branch pushed to remote${NC}"
            else
                echo -e "${YELLOW}⚠️ Push failed or remote not configured${NC}"
            fi
        fi
    else
        echo -e "${RED}❌ Git not available${NC}"
    fi
else
    echo -e "${BLUE}⏭️ Branch setup skipped${NC}"
    PREFLIGHT_RESULTS[branch]=true
fi

# 5. Final Report
echo -e "\n${MAGENTA}📊 PRE-FLIGHT REPORT${NC}"
echo -e "${MAGENTA}===================${NC}"

echo -e "Environment: ${BLUE}$ENVIRONMENT${NC}"

# Check each result
if [[ "${PREFLIGHT_RESULTS[freeze_flag]}" == true ]]; then
    echo -e "Credits Freeze Flag: ${GREEN}✅ SET${NC}"
else
    echo -e "Credits Freeze Flag: ${RED}❌ FAILED${NC}"
fi

if [[ "${PREFLIGHT_RESULTS[backup]}" == true ]]; then
    echo -e "Database Backup: ${GREEN}✅ CREATED${NC}"
else
    echo -e "Database Backup: ${RED}❌ FAILED${NC}"
fi

if [[ "${PREFLIGHT_RESULTS[secrets]}" == true ]]; then
    echo -e "Environment Secrets: ${GREEN}✅ COMPLETE${NC}"
else
    echo -e "Environment Secrets: ${RED}❌ MISSING${NC}"
fi

if [[ "${PREFLIGHT_RESULTS[branch]}" == true ]]; then
    echo -e "Git Branch: ${GREEN}✅ READY${NC}"
else
    echo -e "Git Branch: ${RED}❌ FAILED${NC}"
fi

# Check if all tasks completed
ALL_GOOD=true
for result in "${PREFLIGHT_RESULTS[@]}"; do
    if [[ "$result" != true ]]; then
        ALL_GOOD=false
        break
    fi
done

if [[ "$ALL_GOOD" == true ]]; then
    echo -e "\n${GREEN}🎉 PRE-FLIGHT COMPLETE - READY FOR CREDITS V2 IMPLEMENTATION!${NC}"
else
    echo -e "\n${YELLOW}⚠️ PRE-FLIGHT INCOMPLETE - PLEASE RESOLVE ISSUES ABOVE${NC}"
fi

echo -e "\n${BLUE}Next Steps:${NC}"
echo -e "${NC}1. Verify freeze flag is active in frontend${NC}"
echo -e "${NC}2. Test that credit purchases are disabled${NC}"
echo -e "${NC}3. Begin credits v2 implementation${NC}"
echo -e "${NC}4. Monitor production for any freeze-related issues${NC}"

# Exit with appropriate code
if [[ "$ALL_GOOD" == true ]]; then
    exit 0
else
    exit 1
fi
