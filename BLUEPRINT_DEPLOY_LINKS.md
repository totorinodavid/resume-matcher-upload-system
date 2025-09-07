# 🚀 RENDER BLUEPRINT - Direct Links

## Quick Deploy Links:

### Option 1: Fresh Service (Recommended)
https://dashboard.render.com/blueprints/new?repo=https://github.com/totorinodavid/resume-matcher-upload-system&branch=main&blueprint=render-fresh.yaml

### Option 2: Clean Service
https://dashboard.render.com/blueprints/new?repo=https://github.com/totorinodavid/resume-matcher-upload-system&branch=main&blueprint=render-clean.yaml

### Option 3: Simple Service (No Pre-Deploy)
https://dashboard.render.com/blueprints/new?repo=https://github.com/totorinodavid/resume-matcher-upload-system&branch=main&blueprint=render-simple.yaml

## What Each Does:

### render-fresh.yaml ⭐ BEST
- Service: `nextjs-file-upload-api`
- Full migration support
- Disk storage included
- Health checks configured

### render-clean.yaml
- Service: `upload-api-clean`
- Similar to fresh but different name

### render-simple.yaml
- Service: `simple-upload-api`
- NO pre-deploy command
- Manual migration after deploy

## Expected Deploy Time: ~2-3 minutes
- Build: ~60 seconds (we know this works)
- Deploy: ~30 seconds
- Database setup: ~30 seconds
- Service start: ~30 seconds
