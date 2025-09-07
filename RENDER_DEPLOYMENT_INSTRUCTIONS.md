# 🚀 RENDER DEPLOYMENT - Manual Fallback

## If Blueprint render-fresh.yaml not detected:

### 1. Create New Web Service
- Repository: `totorinodavid/resume-matcher-upload-system`
- Branch: `main`
- **Root Directory: `apps/backend-clean`** ⚠️

### 2. Build Settings
```
Build Command: npm install && npm run build
Start Command: npm start -p $PORT
```

### 3. Environment Variables
```
NODE_ENV=production
DATABASE_URL=[from PostgreSQL database]
UPLOAD_DIR=/tmp/uploads
```

### 4. SKIP Pre-Deploy Command Initially
- Deploy first without pre-deploy
- Run migrations manually after service is up:
  ```bash
  # In Render Shell
  npm run migrate
  ```

### 5. Add Disk Storage (Optional)
```
Name: upload-files
Mount Path: /tmp/uploads
Size: 1GB
```

## Expected Result:
✅ Service: https://[your-service-name].onrender.com
✅ Health: https://[your-service-name].onrender.com/api/health
✅ Upload API: https://[your-service-name].onrender.com/api/upload
