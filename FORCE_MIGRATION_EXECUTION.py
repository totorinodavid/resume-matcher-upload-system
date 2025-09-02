#!/usr/bin/env python3
"""
FORCE MIGRATION EXECUTION - Trigger new deployment with explicit migration
"""
import subprocess
import os
from datetime import datetime

def force_migration_deployment():
    """Force a new deployment that will execute the migration"""
    
    print(f"🚨 FORCE MIGRATION DEPLOYMENT - {datetime.now()}")
    print("=" * 60)
    
    # Add a timestamp to force git change
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Update render.yaml to force migration
    render_yaml_content = '''# Render Blueprint for Resume Matcher backend with PostgreSQL
# Docs: https://render.com/docs/blueprint-spec
# MIGRATION FORCED: {timestamp}

# PostgreSQL Database für Resume Matcher - FREE PLAN für Testing
databases:
  - name: resume-matcher-db
    databaseName: resume_matcher
    user: resume_user
    plan: free  # 256MB RAM, 0.1 CPU, 1GB Storage - Perfect für Testing
    postgresMajorVersion: 15

services:
  - name: resume-matcher-backend
    type: web
    runtime: docker

    # Build from the repo's Dockerfile at the root
    dockerfilePath: ./Dockerfile
    dockerContext: .

    # 🚨 FORCE MIGRATION EXECUTION - Run Alembic migrations before each deploy
    preDeployCommand: >-
      echo "FORCING MIGRATION EXECUTION..." &&
      cd /app/apps/backend && 
      echo "Current directory: $(pwd)" && 
      echo "Python path: $(which python)" && 
      echo "Alembic config exists: $(ls -la alembic.ini)" &&
      python -m alembic current &&
      echo "Running migration upgrade..." &&
      python -m alembic upgrade head &&
      echo "Migration completed successfully!"

    # Start FastAPI via Uvicorn using traditional Python, binding to Render's $PORT
    dockerCommand: >-
      cd /app/apps/backend && python serve.py

    # Health check for zero-downtime deploys
    healthCheckPath: /healthz

    # Auto-deploy on commits to the linked branch
    autoDeployTrigger: commit

    # Instance size and count - FREE PLAN für Testing
    plan: free  # 512MB RAM, 0.1 CPU - Ausreichend für Testing
    numInstances: 1

    # Environment variables (database URL automatically injected from database)
    envVars:
      # Database - automatically injected from resume-matcher-db
      - key: DATABASE_URL
        fromDatabase:
          name: resume-matcher-db
          property: connectionString
      - key: ASYNC_DATABASE_URL
        fromDatabase:
          name: resume-matcher-db
          property: connectionString
      
      # Emergency fallback for manual configuration
      - key: FALLBACK_DATABASE_URL
        sync: false  # Set manually in dashboard if auto-injection fails
      
      # Manual override for testing (leave empty if auto-injection works)
      - key: MANUAL_DATABASE_URL
        sync: false  # For manual database URL override
      
      # Session und Auth
      - key: SESSION_SECRET_KEY
        sync: false  # Set in dashboard
      - key: NEXTAUTH_SECRET
        sync: false  # Set in dashboard  
      - key: NEXTAUTH_URL
        value: https://gojob.ing
      
      # Stripe (optional für Testphase)
      - key: STRIPE_SECRET_KEY
        sync: false
      - key: STRIPE_WEBHOOK_SECRET
        sync: false
      
      # Stripe price→credits mapping
      - key: STRIPE_PRICE_SMALL_ID
        sync: false
      - key: STRIPE_PRICE_SMALL_CREDITS
        value: "100"
      - key: STRIPE_PRICE_MEDIUM_ID
        sync: false
      - key: STRIPE_PRICE_MEDIUM_CREDITS
        value: "500"
      - key: STRIPE_PRICE_LARGE_ID
        sync: false
      - key: STRIPE_PRICE_LARGE_CREDITS
        value: "1500"
      
      # AI configuration
      - key: LLM_PROVIDER
        value: openai
      - key: LLM_MODEL
        value: gpt-4o-mini
      - key: LLM_API_KEY
        sync: false  # OpenAI API Key
      - key: OPENAI_API_KEY
        sync: false  # Fallback
      - key: EMBEDDING_PROVIDER
        value: openai
      - key: EMBEDDING_MODEL
        value: text-embedding-3-small
      - key: EMBEDDING_API_KEY
        sync: false
      
      # Environment
      - key: ENV
        value: production
      - key: LOG_LEVEL
        value: info
      - key: PYTHONUNBUFFERED
        value: "1"
      - key: PYTHONPATH
        value: /app/apps/backend
      - key: ALEMBIC_CONFIG
        value: /app/apps/backend/alembic.ini
      - key: ALLOWED_ORIGINS
        value: '["https://gojob.ing","https://www.gojob.ing","http://localhost:3000"]'
      
      # 🚨 EMERGENCY: Enable E2E test mode for webhook testing
      - key: E2E_TEST_MODE
        value: "true"
'''.format(timestamp=timestamp)
    
    # Write updated render.yaml
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_yaml_content)
    print("✅ Updated render.yaml with forced migration command")
    
    # Git operations
    print("\n📦 Committing changes...")
    subprocess.run(['git', 'add', 'render.yaml'], check=True)
    subprocess.run(['git', 'commit', '-m', f'🚨 FORCE MIGRATION: Enhanced migration execution with debugging - {timestamp}'], check=True)
    
    print("\n🚀 Pushing to trigger deployment...")
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Git push successful!")
        print("🎯 Deployment triggered on Render")
        print("⏱️  Migration will run with enhanced debugging")
        print("\n📋 Next steps:")
        print("1. Monitor Render deployment logs")
        print("2. Check for migration execution output")  
        print("3. Verify credits_balance column exists")
        print("4. Test webhook functionality")
        return True
    else:
        print(f"❌ Git push failed: {result.stderr}")
        return False

if __name__ == "__main__":
    force_migration_deployment()
