# RENDER MCP AUTOMATED DEPLOYMENT GUIDE

## 1. API KEY SETUP
1. Go to: https://dashboard.render.com/account/api-keys
2. Click "Create API Key"
3. Name: "MCP-Automation"  
4. Copy the API key

## 2. MCP CONFIGURATION
Add to your AI tool's MCP configuration file:

### For Cursor (~/.cursor/mcp.json):
```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_RENDER_API_KEY_HERE"
      }
    }
  }
}
```

### For Claude Desktop (claude_desktop_config.json):
```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_RENDER_API_KEY_HERE"
      }
    }
  }
}
```

## 3. AUTOMATED DEPLOYMENT PROMPTS

### Initial Setup:
"Set my Render workspace to [YOUR_WORKSPACE_NAME]"

### Complete Service Creation:
"Create a new web service with these specifications:
- Name: resume-matcher-auto
- Repository: https://github.com/totorinodavid/resume-matcher-upload-system
- Branch: security-hardening-neon
- Root Directory: apps/backend-clean
- Build Command: npm ci && npm run build
- Start Command: npm start
- Auto-deploy: enabled"

### Database Creation:
"Create a PostgreSQL database named 'resume-matcher-db' with 1GB storage"

### Environment Variables:
"Set these environment variables for resume-matcher-auto service:
- NODE_ENV=production
- DATABASE_URL=[get from database]
- ADMIN_PASSWORD=[secure password]
- UPLOAD_DIR=/opt/render/project/src/uploads"

### Persistent Disk:
"Add a persistent disk to resume-matcher-auto service:
- Name: upload-disk
- Size: 10GB
- Mount Path: /opt/render/project/src/uploads"

## 4. MONITORING & MANAGEMENT PROMPTS

### Service Status:
"Show me the status of my resume-matcher-auto service"

### Deployment Logs:
"Show me the latest deployment logs for resume-matcher-auto"

### Error Troubleshooting:
"Why is my resume-matcher-auto service failing? Show me error logs"

### Metrics:
"Show me CPU and memory usage for resume-matcher-auto from the last 24 hours"

### Updates:
"Redeploy my resume-matcher-auto service"
"Update environment variable ADMIN_PASSWORD for resume-matcher-auto to [new-password]"

## 5. AUTOMATED WORKFLOW
With MCP configured, you can now manage your entire Render infrastructure through AI prompts:

1. ✅ Create services automatically
2. ✅ Configure databases  
3. ✅ Set environment variables
4. ✅ Monitor deployments
5. ✅ Troubleshoot issues
6. ✅ Scale services
7. ✅ Manage updates

## READY TO USE:
Once MCP is configured, simply prompt your AI tool with any of the commands above and it will automatically execute them via the Render API!
