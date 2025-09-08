FROM node:18-alpine AS base
WORKDIR /app
ENV NODE_ENV=production \
		FILES_DIR=/var/data

FROM base AS deps
# Need openssl for prisma engine download
RUN apk add --no-cache openssl
COPY package*.json ./
COPY prisma ./prisma/
RUN npm ci --omit=dev
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
COPY --from=build /app/public ./public
COPY --from=build /app/apps/backend-clean/lib ./apps/backend-clean/lib
COPY --from=build /app/apps/backend-clean/app ./apps/backend-clean/app
COPY --from=build /app/apps/backend-clean/middleware.ts ./apps/backend-clean/middleware.ts

# Ensure data directory exists
RUN mkdir -p /var/data && chmod 755 /var/data

# Simple entrypoint to run migrations before start (best-effort)
COPY <<'EOF' /app/entrypoint.sh
#!/bin/sh
set -e
if [ -f prisma/schema.prisma ]; then
	npx prisma migrate deploy || echo "[warn] prisma migrate deploy failed"
fi
exec npm start
EOF
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
