FROM node:18-alpine AS base
WORKDIR /app
ENV NODE_ENV=production \
		FILES_DIR=/var/data

FROM base AS deps
# Need openssl for prisma engine download
RUN apk add --no-cache openssl
COPY package*.json ./
COPY prisma ./prisma/
RUN npm ci
RUN npx prisma generate

FROM deps AS build
ENV NODE_ENV=production
COPY . .
RUN npm run build

FROM base AS runtime
RUN apk add --no-cache openssl
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/prisma ./prisma
COPY --from=build /app/.next ./.next
COPY --from=build /app/package*.json ./
COPY --from=build /app/next.config.* ./
# Copy application source (already compiled into .next). These source copies are only needed for runtime
# utilities referenced outside the compiled bundle (currently none strictly required). We include them for
# transparency / potential runtime inspection. Adjusted paths because build context already is backend-clean.
COPY --from=build /app/lib ./lib
COPY --from=build /app/app ./app
COPY --from=build /app/middleware.ts ./middleware.ts
# Public assets (optional). If directory doesn't exist, create empty one to avoid copy failures.
RUN mkdir -p public

# Ensure data directory exists
RUN mkdir -p /var/data && chmod 755 /var/data

# Simple entrypoint to run migrations before start (best-effort)
COPY <<'EOF' /app/entrypoint.sh
#!/bin/sh
set -e
if [ -f prisma/schema.prisma ]; then
	npx prisma migrate deploy || echo "[warn] prisma migrate deploy failed"
fi
echo "[boot] validating required environment..."
# Minimal preflight env validation (avoid requiring TS sources directly before Next starts).
node -e "['DATABASE_URL'].forEach(n=>{if(!process.env[n]||!process.env[n].trim()){console.error('[fatal] missing env '+n);process.exit(1)}});console.log('[boot] env ok')" || { echo '[fatal] config validation failed'; exit 1; }
exec npm start
EOF
RUN chmod +x /app/entrypoint.sh

RUN npm prune --omit=dev

ENTRYPOINT ["/app/entrypoint.sh"]
