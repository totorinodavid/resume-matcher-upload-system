FROM node:18-alpine AS base
WORKDIR /app
ENV NODE_ENV=production \
		FILES_DIR=/var/data

# ----- Build stage (monorepo root context) -----
FROM base AS build
RUN apk add --no-cache openssl
# Copy only backend-clean manifest first for layer cache
COPY apps/backend-clean/package*.json ./
COPY apps/backend-clean/prisma ./prisma/
RUN npm ci
# Copy backend source code
COPY apps/backend-clean .
RUN npx prisma generate
ENV NODE_ENV=production
RUN npm run build

# ----- Runtime stage -----
FROM base AS runtime
RUN apk add --no-cache openssl
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/.next ./.next
COPY --from=build /app/package*.json ./
COPY --from=build /app/next.config.* ./
COPY --from=build /app/public ./public
RUN [ -d public ] || mkdir -p public
COPY --from=build /app/lib ./lib
COPY --from=build /app/app ./app
COPY --from=build /app/middleware.ts ./middleware.ts
RUN mkdir -p /var/data && chmod 755 /var/data

COPY <<'EOF' /app/entrypoint.sh
#!/bin/sh
set -e
if [ -f prisma/schema.prisma ]; then
	npx prisma migrate deploy || echo "[warn] prisma migrate deploy failed"
fi
echo "[boot] validating required environment..."
node -e "['DATABASE_URL'].forEach(n=>{if(!process.env[n]||!process.env[n].trim()){console.error('[fatal] missing env '+n);process.exit(1)}});console.log('[boot] env ok')" || { echo '[fatal] config validation failed'; exit 1; }
exec npm start
EOF
RUN chmod +x /app/entrypoint.sh

RUN npm prune --omit=dev

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
	CMD wget -q -O /dev/null "http://127.0.0.1:${PORT:-3000}/api/health" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
