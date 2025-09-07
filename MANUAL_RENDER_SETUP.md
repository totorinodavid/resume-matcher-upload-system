# 🚀 MANUAL SERVICE CREATION - Step by Step

## If Blueprint doesn't work, create manually:

### 1. New Web Service (NOT Blueprint)
- Go to: https://dashboard.render.com/services/new/web
- Repository: totorinodavid/resume-matcher-upload-system
- Branch: main

### 2. Service Configuration:
```
Name: nextjs-file-upload-api
Root Directory: apps/backend-clean
Runtime: Node
Build Command: npm install && npm run build
Start Command: npm start
```

### 3. Environment Variables:
```
NODE_ENV=production
UPLOAD_DIR=/tmp/uploads
DATABASE_URL=[will be set after DB creation]
```

### 4. Create PostgreSQL Database Separately:
- Name: upload-files-db
- Database Name: uploads
- User: uploads_user
- Plan: Free

### 5. Connect Database:
- Copy DATABASE_URL from database
- Add to service environment variables

### 6. Deploy & Run Migrations:
```bash
# After first deploy, in Render shell:
npx prisma migrate deploy
```

## Expected URL:
https://nextjs-file-upload-api.onrender.com
