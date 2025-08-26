Deployment guide (private repo)

Frontend (Vercel)
- Set GitHub repo secrets:
  - VERCEL_TOKEN
  - VERCEL_ORG_ID
  - VERCEL_PROJECT_ID
- The workflow .github/workflows/frontend-vercel.yml runs on push to security-hardening-neon and deploys via Vercel CLI.

Backend (Render)
- Create a Render Web Service or Blueprint from render.yaml.
- Get the Deploy Hook URL from Render and set GitHub repo secret RENDER_DEPLOY_HOOK_URL.
- The workflow .github/workflows/backend-render.yml will POST to that hook on push.

Notes
- .gitignore already prevents committing .env, local DBs, and env folders.
- Adjust branches in the workflows if you change your default branch.