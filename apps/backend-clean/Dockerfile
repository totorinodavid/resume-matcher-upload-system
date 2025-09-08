FROM node:18-alpine

# Install OpenSSL for Prisma
RUN apk add --no-cache openssl curl

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY prisma ./prisma/

# Install dependencies
RUN npm install --omit=dev

# Generate Prisma Client
RUN npx prisma generate

# Copy app code
COPY . .

# Build Next.js
RUN npm run build

# Create uploads directory
RUN mkdir -p /var/data && chmod 755 /var/data

EXPOSE 4000

CMD ["npm", "run", "start"]
