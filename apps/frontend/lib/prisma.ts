import { PrismaClient } from '@prisma/client'

declare global {
  // eslint-disable-next-line no-var
  var __prisma: PrismaClient | undefined
}

// Database configuration for Resume Matcher
// Production: Use pooled connection for Render/Neon
// Development: Use direct connection
const getDatabaseUrl = () => {
  const DATABASE_URL = process.env.DATABASE_URL
  const DATABASE_POOL_URL = process.env.DATABASE_POOL_URL
  
  // During build time or when DATABASE_URL is not available
  if (!DATABASE_URL) {
    // Check if we're in build phase
    if (process.env.NEXT_PHASE === 'phase-production-build' || 
        process.env.NODE_ENV === 'development' ||
        typeof window !== 'undefined') {
      // Return a dummy URL during build time
      return 'postgresql://dummy:dummy@dummy:5432/dummy'
    }
    throw new Error('DATABASE_URL environment variable is required for runtime')
  }
  
  // Use pooled connection in production, direct in development
  const databaseUrl = process.env.NODE_ENV === 'production' && DATABASE_POOL_URL 
    ? DATABASE_POOL_URL 
    : DATABASE_URL
  
  // Ensure SSL is enabled for production PostgreSQL
  const urlWithSSL = databaseUrl.includes('sslmode') 
    ? databaseUrl 
    : `${databaseUrl}?sslmode=require`
    
  return urlWithSSL
}

// Create Prisma client with Resume Matcher optimizations
const createPrismaClient = () => {
  try {
    return new PrismaClient({
      datasources: {
        db: {
          url: getDatabaseUrl()
        }
      },
      log: process.env.NODE_ENV === 'development' 
        ? ['query', 'error', 'warn'] 
        : ['error'],
    })
  } catch (error) {
    // During build time, return a mock client
    if (process.env.NEXT_PHASE === 'phase-production-build') {
      console.warn('Using mock Prisma client during build')
      return {} as PrismaClient
    }
    throw error
  }
}

// Lazy singleton pattern for Prisma client
let _prisma: PrismaClient | undefined

const getPrismaClient = () => {
  if (!_prisma) {
    _prisma = globalThis.__prisma ?? createPrismaClient()
    if (process.env.NODE_ENV !== 'production') {
      globalThis.__prisma = _prisma
    }
  }
  return _prisma
}

// Export lazy getter instead of direct instance
export const prisma = new Proxy({} as PrismaClient, {
  get(target, prop) {
    const client = getPrismaClient()
    const value = client[prop as keyof PrismaClient]
    return typeof value === 'function' ? value.bind(client) : value
  }
})

export default prisma