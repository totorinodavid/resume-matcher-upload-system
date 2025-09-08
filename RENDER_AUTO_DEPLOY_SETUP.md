# Render Service Configuration with Personal Access Token
# 
# Setup Instructions:
# 1. Create GitHub Personal Access Token at: https://github.com/settings/tokens
# 2. Select scopes: 'repo' and 'workflow'
# 3. Copy the token
# 4. In Render Dashboard:
#    - New Web Service
#    - Connect repository with URL: https://YOUR_TOKEN@github.com/totorinodavid/resume-matcher-upload-system
#    - Branch: security-hardening-neon
#    - Root Directory: apps/backend-clean

Repository URL with Token:
https://YOUR_GITHUB_TOKEN@github.com/totorinodavid/resume-matcher-upload-system

Service Configuration:
- Name: resume-matcher-auto
- Branch: security-hardening-neon  
- Root Directory: apps/backend-clean
- Build Command: npm ci && npm run build
- Start Command: npm start
- Auto-Deploy: Yes

Environment Variables:
NODE_ENV=production
DATABASE_URL=<your-postgres-connection-string>
ADMIN_PASSWORD=<secure-password>
UPLOAD_DIR=/opt/render/project/src/uploads

Persistent Disk:
- Name: upload-disk
- Mount Path: /opt/render/project/src/uploads
- Size: 10GB
