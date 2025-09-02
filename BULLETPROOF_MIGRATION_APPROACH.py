#!/usr/bin/env python3
"""
BULLETPROOF MIGRATION: Alternative approach using startup command integration
Based on Render community findings - preDeployCommand sometimes fails in Docker contexts
"""
import subprocess
import os
from datetime import datetime

def create_startup_migration_approach():
    """Create a bulletproof approach by integrating migration into the startup process"""
    
    print(f"🚨 BULLETPROOF MIGRATION APPROACH - {datetime.now()}")
    print("=" * 60)
    print("📋 Creating startup-integrated migration solution...")
    
    # 1. Create a startup script that runs migration then starts the app
    startup_script = '''#!/bin/bash
set -e

echo "🚨 STARTUP MIGRATION EXECUTION..."
echo "Current directory: $(pwd)"
echo "Python executable: $(which python)"
echo "Environment variables:"
env | grep -E "(DATABASE|ASYNC)" || echo "No database env vars found"

cd /app/apps/backend

echo "📋 Checking Alembic setup..."
if [ -f "alembic.ini" ]; then
    echo "✅ alembic.ini found"
    cat alembic.ini | head -20
else
    echo "❌ alembic.ini not found"
    ls -la
fi

echo "🔍 Running Alembic current..."
python -m alembic current || echo "Failed to get current revision"

echo "🚀 Running Alembic migration..."
python -m alembic upgrade head

echo "✅ Migration completed, starting application..."
exec python serve.py
'''
    
    with open('startup_with_migration.sh', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    # Make it executable
    os.chmod('startup_with_migration.sh', 0o755)
    print("✅ Created startup_with_migration.sh")
    
    # 2. Update render.yaml to use startup script instead of preDeployCommand
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    render_yaml_content = f'''# Render Blueprint - BULLETPROOF MIGRATION APPROACH
# Migration integrated into startup process - {timestamp}

databases:
  - name: resume-matcher-db
    databaseName: resume_matcher
    user: resume_user
    plan: free
    postgresMajorVersion: 15

services:
  - name: resume-matcher-backend
    type: web
    runtime: docker

    # Build from the repo's Dockerfile
    dockerfilePath: ./Dockerfile
    dockerContext: .

    # 🚨 BULLETPROOF: NO preDeployCommand - migration runs in startup script
    # preDeployCommand removed - causes issues in Docker environments

    # Use startup script that runs migration then starts app
    dockerCommand: >-
      chmod +x /app/startup_with_migration.sh && /app/startup_with_migration.sh

    healthCheckPath: /healthz
    autoDeployTrigger: commit
    plan: free
    numInstances: 1

    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: resume-matcher-db
          property: connectionString
      - key: ASYNC_DATABASE_URL
        fromDatabase:
          name: resume-matcher-db
          property: connectionString
      
      # Session und Auth
      - key: SESSION_SECRET_KEY
        sync: false
      - key: NEXTAUTH_SECRET
        sync: false
      - key: NEXTAUTH_URL
        value: https://gojob.ing
      
      # Stripe
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
        sync: false
      - key: OPENAI_API_KEY
        sync: false
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
        value: '[\"https://gojob.ing\",\"https://www.gojob.ing\",\"http://localhost:3000\"]'
      
      # Emergency test mode
      - key: E2E_TEST_MODE
        value: "true"
'''
    
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(render_yaml_content)
    print("✅ Updated render.yaml with startup migration approach")
    
    # 3. Update Dockerfile to copy startup script
    dockerfile_content = '''# Use Python 3.12 slim image for better performance
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY apps/backend/requirements.txt /app/apps/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/apps/backend/requirements.txt

# Copy application code
COPY . /app/

# Copy startup script
COPY startup_with_migration.sh /app/startup_with_migration.sh
RUN chmod +x /app/startup_with_migration.sh

# Set Python path
ENV PYTHONPATH=/app/apps/backend

# Expose port
EXPOSE 8000

# Default command (will be overridden by render.yaml)
CMD ["/app/startup_with_migration.sh"]
'''
    
    with open('Dockerfile', 'w', encoding='utf-8') as f:
        f.write(dockerfile_content)
    print("✅ Updated Dockerfile to include startup script")
    
    # 4. Git operations
    print("\\n📦 Committing bulletproof migration approach...")
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', f'🚨 BULLETPROOF MIGRATION: Startup-integrated approach - {timestamp}'], check=True)
    
    print("\\n🚀 Pushing bulletproof solution...")
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Git push successful!")
        print("🎯 BULLETPROOF deployment triggered!")
        print("\\n🔧 What this approach does:")
        print("1. ❌ Removes problematic preDeployCommand")
        print("2. ✅ Integrates migration into startup script")
        print("3. ✅ Migration runs BEFORE app starts")
        print("4. ✅ Uses Docker CMD for reliable execution")
        print("5. ✅ Better error handling and logging")
        print("\\n⏱️  Expected result:")
        print("- Migration will run during container startup")
        print("- credits_balance column will be created")
        print("- Database errors will disappear")
        print("- Stripe webhooks will work")
        return True
    else:
        print(f"❌ Git push failed: {result.stderr}")
        return False

if __name__ == "__main__":
    create_startup_migration_approach()
