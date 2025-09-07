#!/bin/bash
# AUTOMATISCHES RENDER DEPLOYMENT SCRIPT

echo "🚀 Starting Render Deployment..."

# 1. PostgreSQL Database erstellen (API Call)
curl -X POST \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  https://api.render.com/v1/services \
  -d '{
    "type": "pserv",
    "name": "resume-matcher-db",
    "plan": "starter",
    "region": "frankfurt",
    "databaseName": "resume_matcher",
    "databaseUser": "resume_user"
  }'

echo "✅ PostgreSQL Database created"

# 2. Backend Web Service erstellen  
curl -X POST \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  https://api.render.com/v1/services \
  -d '{
    "type": "web_service",
    "name": "resume-matcher-backend",
    "repo": "https://github.com/ririyg420/resume-matcher-private",
    "branch": "security-hardening-neon",
    "rootDir": "apps/backend",
    "buildCommand": "npm install && npx prisma generate && npm run build",
    "startCommand": "npm run start",
    "plan": "starter",
    "region": "frankfurt",
    "envVars": [
      {"key": "NODE_ENV", "value": "production"},
      {"key": "FILES_DIR", "value": "/var/data"},
      {"key": "ADMIN_TOKEN", "value": "secure-admin-token-2024"}
    ]
  }'

echo "✅ Backend Service created"
echo "🎉 Deployment initiated!"
