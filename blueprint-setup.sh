#!/usr/bin/env bash

# RENDER BLUEPRINT MANUAL SETUP GUIDE
# Infrastructure-as-Code Deployment for Resume Matcher

echo "🎯 RENDER BLUEPRINT SETUP GUIDE"
echo "=============================="
echo ""

echo "📋 BLUEPRINT OVERVIEW:"
echo "- Render Blueprints = Infrastructure as Code"
echo "- Uses render.yaml file for service definition"
echo "- Automatic deployment on git push"
echo "- Proper runtime configuration"
echo ""

echo "🔧 SETUP STEPS:"
echo "1. Go to: https://dashboard.render.com/blueprints"
echo "2. Click 'New Blueprint'"
echo "3. Connect GitHub Repository:"
echo "   Repository: totorinodavid/resume-matcher-upload-system"
echo "   Branch: security-hardening-neon"
echo ""

echo "📁 BLUEPRINT CONFIGURATION:"
echo "- File: render.yaml (already exists in root)"
echo "- Service: resume-matcher-backend"
echo "- Runtime: Node.js"
echo "- Root Directory: apps/backend-clean"
echo "- Build Command: npm install"
echo "- Start Command: npm start"
echo ""

echo "🔄 AUTOMATIC DEPLOYMENT:"
echo "- Blueprint syncs on every git push"
echo "- Service updates automatically"
echo "- Database migration runs on deploy"
echo "- Environment variables preserved"
echo ""

echo "✅ BLUEPRINT ADVANTAGES:"
echo "- ✓ Correct Node.js runtime (not Docker)"
echo "- ✓ Clean backend directory"
echo "- ✓ Automatic deployments"
echo "- ✓ Infrastructure versioning"
echo "- ✓ No API limitations"
echo ""

echo "🌐 NEXT ACTIONS:"
echo "1. Visit: https://dashboard.render.com/blueprints"
echo "2. Create Blueprint from GitHub repository"
echo "3. Blueprint will use existing render.yaml"
echo "4. Services deploy automatically"
echo ""

echo "📋 CURRENT render.yaml CONFIG:"
cat << 'EOF'
services:
  - type: web
    name: resume-matcher-backend
    runtime: node
    rootDir: apps/backend-clean
    buildCommand: npm install
    startCommand: npm start
    plan: free
    branch: security-hardening-neon
    disk:
      name: uploads-disk
      mountPath: /opt/render/project/src/uploads
      sizeGB: 10
    envVars:
      - key: NODE_ENV
        value: production
      - key: DATABASE_URL
        fromDatabase:
          name: resume-matcher-db
          property: connectionString
      - key: NEXTAUTH_SECRET
        generateValue: true
      - key: NEXTAUTH_URL
        value: https://resume-matcher-backend.onrender.com

databases:
  - name: resume-matcher-db
    databaseName: resume_matcher
    user: resume_matcher_user
    plan: free
    postgresMajorVersion: 15
EOF

echo ""
echo "🎉 BLUEPRINT READY FOR DEPLOYMENT!"
echo "=============================="
