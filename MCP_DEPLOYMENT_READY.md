# RENDER MCP AUTOMATED DEPLOYMENT - READY TO USE

## ✅ CONFIGURATION COMPLETE
- API Key: rnd_fuLBqqLoUnK7cQdnORYYoYLKBFIT
- MCP Server: https://mcp.render.com/mcp
- Configuration: .cursor/mcp.json

## 🚀 IMMEDIATE DEPLOYMENT COMMANDS

### 1. Set Workspace (FIRST COMMAND):
```
Set my Render workspace to [YOUR_WORKSPACE_NAME]
```

### 2. Complete Automated Service Creation:
```
Create a new web service with these exact specifications:
- Service name: resume-matcher-auto
- Repository URL: https://github.com/totorinodavid/resume-matcher-upload-system
- Branch: security-hardening-neon
- Root directory: apps/backend-clean
- Build command: npm ci && npm run build
- Start command: npm start
- Runtime: Node.js 18
- Auto-deploy: enabled
- Health check path: /api/health
```

### 3. Create Database:
```
Create a PostgreSQL database named 'resume-matcher-db' with 1GB storage
```

### 4. Configure Environment Variables:
```
Set these environment variables for the resume-matcher-auto service:
NODE_ENV=production
DATABASE_URL=[connection string from resume-matcher-db]
ADMIN_PASSWORD=SecurePassword123!
UPLOAD_DIR=/opt/render/project/src/uploads
```

### 5. Add Persistent Storage:
```
Add a persistent disk to resume-matcher-auto service:
- Disk name: upload-disk
- Size: 10GB
- Mount path: /opt/render/project/src/uploads
```

## 🔍 MONITORING COMMANDS

### Check Deployment Status:
```
Show me the deployment status and recent logs for resume-matcher-auto service
```

### Monitor Health:
```
Check the health endpoint /api/health for resume-matcher-auto and show me any errors
```

### View Metrics:
```
Show me CPU, memory, and response time metrics for resume-matcher-auto from the last hour
```

## 🛠️ TROUBLESHOOTING COMMANDS

### Build Issues:
```
Why is my resume-matcher-auto service failing to build? Show me the build logs and errors
```

### Runtime Errors:
```
Show me the latest error logs for resume-matcher-auto service and help me diagnose the issue
```

### Database Connection:
```
Test the database connection for resume-matcher-auto and show me any connectivity issues
```

## 📋 DEPLOYMENT CHECKLIST

After running the commands above, verify:
- [ ] Service is running at: https://resume-matcher-auto.onrender.com
- [ ] Health check responds: https://resume-matcher-auto.onrender.com/api/health
- [ ] Database is connected and accessible
- [ ] Upload directory is mounted and writable
- [ ] Auto-deploy triggers on Git pushes
- [ ] Environment variables are set correctly

## 🎯 READY TO DEPLOY!

You can now copy and paste any of the commands above into your AI chat to automatically deploy and manage your Resume Matcher service on Render!

Start with setting your workspace, then run the service creation command.
