FROM node:18-alpine

# Install OpenSSL for Prisma
RUN apk add --no-cache openssl curl

WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./
COPY prisma ./prisma/

# Install only production dependencies
RUN npm install --omit=dev

# Generate Prisma Client (needs schema + node_modules)
RUN npx prisma generate

# Copy remaining application code
COPY . .

# Build Next.js
RUN npm run build

# Runtime environment vars (Render will still inject its own PORT)
ENV FILES_DIR=/var/data \
	NODE_ENV=production

# Ensure data directory exists (kept outside repo for persistence when using volumes)
RUN mkdir -p /var/data && chmod 755 /var/data

# Do NOT hardcode or expose a fixed port; Render/other PaaS set $PORT which Next.js picks up.
# EXPOSE omitted intentionally to avoid misleading static port assumptions.

CMD ["npm", "start"]
