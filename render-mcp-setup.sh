# Render MCP Server Automation Script
# This script helps automate Render service management via MCP

# Step 1: Create Render API Key
# Go to: https://dashboard.render.com/account/api-keys
# Create new API key with name: "MCP-Automation"

# Step 2: Configure MCP in your AI tool
# For Cursor: Add to ~/.cursor/mcp.json
# For Claude Desktop: Add to claude_desktop_config.json

# Step 3: Example MCP prompts for automatic deployment:

## SERVICE CREATION PROMPTS:
# "Create a new web service named 'resume-matcher-auto' using repository 'https://github.com/totorinodavid/resume-matcher-upload-system' on branch 'security-hardening-neon' with root directory 'apps/backend-clean'"

# "Set up environment variables for my resume-matcher-auto service: NODE_ENV=production, UPLOAD_DIR=/opt/render/project/src/uploads"

# "Create a PostgreSQL database named 'resume-matcher-db' with 1GB storage"

# "Add a persistent disk named 'upload-disk' with 10GB storage to my resume-matcher-auto service, mounted at '/opt/render/project/src/uploads'"

## MONITORING PROMPTS:
# "Show me the deployment status of my resume-matcher-auto service"
# "What are the recent logs for my resume-matcher-auto service?"
# "Show me the metrics for my resume-matcher-auto service from the last 24 hours"

## TROUBLESHOOTING PROMPTS:
# "Why is my resume-matcher-auto service failing to build?"
# "Show me error logs for my resume-matcher-auto service"
# "What's the current health status of all my services?"

## UPDATE PROMPTS:
# "Update the environment variable ADMIN_PASSWORD for my resume-matcher-auto service"
# "Redeploy my resume-matcher-auto service"
# "Scale my resume-matcher-auto service to 2 instances"

# Step 4: Workspace Setup
# First prompt after MCP setup: "Set my Render workspace to [YOUR_WORKSPACE_NAME]"

# Step 5: Automated Deployment Flow
DEPLOYMENT_COMMANDS="
1. Set my Render workspace to [YOUR_WORKSPACE]
2. Create a new web service named 'resume-matcher-auto' using repository 'https://github.com/totorinodavid/resume-matcher-upload-system' on branch 'security-hardening-neon' with root directory 'apps/backend-clean', build command 'npm ci && npm run build', start command 'npm start'
3. Create a PostgreSQL database named 'resume-matcher-db'
4. Set environment variables for resume-matcher-auto: NODE_ENV=production, DATABASE_URL=<database-connection-string>, ADMIN_PASSWORD=<secure-password>, UPLOAD_DIR=/opt/render/project/src/uploads
5. Add persistent disk 'upload-disk' with 10GB storage mounted at '/opt/render/project/src/uploads'
6. Enable auto-deploy for resume-matcher-auto service
"

echo "Render MCP Server setup complete!"
echo "Next: Create API key and configure your AI tool with the MCP configuration"
