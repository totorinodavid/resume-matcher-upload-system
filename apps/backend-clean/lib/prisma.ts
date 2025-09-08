import pkg from '@prisma/client'
const { PrismaClient } = pkg as any

type PrismaClientType = InstanceType<typeof PrismaClient>
const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClientType | undefined
}

export const prisma: PrismaClientType = globalForPrisma.prisma ?? new (PrismaClient as any)({
  log: ['warn', 'error']
})

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma
}

// Graceful shutdown (ensure only registered once in a given process)
let shutdownHookRegistered = (globalThis as any).__PRISMA_SHUTDOWN_REGISTERED__
if (!shutdownHookRegistered) {
  const register = () => {
    const handler = async (signal: string) => {
      try {
        await prisma.$disconnect()
      } finally {
        process.exit(0)
      }
    }
    process.once('SIGTERM', () => handler('SIGTERM'))
    process.once('SIGINT', () => handler('SIGINT'))
    process.once('beforeExit', async () => {
      await prisma.$disconnect()
    })
    ;(globalThis as any).__PRISMA_SHUTDOWN_REGISTERED__ = true
  }
  register()
}
