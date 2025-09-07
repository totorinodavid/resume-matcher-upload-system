# Resume Matcher Upload System - Production Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files and important directories
COPY package*.json ./
COPY prisma ./prisma/
COPY tsconfig.json ./
COPY next.config.js ./

# Install dependencies
RUN npm ci --only=production

# Generate Prisma Client
RUN npx prisma generate

# Copy all application code
COPY . .

# Build Next.js application
RUN npm run build

# Create uploads directory
RUN mkdir -p /var/data

# Set permissions for uploads directory
RUN chmod 755 /var/data

# Expose port
EXPOSE 4000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:4000/api/health || exit 1

# Start command
CMD ["npm", "run", "start"]
