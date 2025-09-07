# Render Deploy Script for Backend
# Run this on Render.com

echo "🚀 Starting Resume Matcher Backend Deployment"

# Install dependencies
echo "📦 Installing dependencies..."
cd apps/backend
npm ci --only=production

# Generate Prisma Client
echo "🔧 Generating Prisma Client..."
npx prisma generate

# Run database migrations
echo "🗄️ Running database migrations..."
npx prisma db push

# Build application
echo "🏗️ Building application..."
npm run build

echo "✅ Deployment complete!"
echo "Backend ready at /api/health"
