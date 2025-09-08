import { PrismaClient } from '@prisma/client'

declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined
}

export const prisma = globalThis.prisma || new PrismaClient()

if (process.env.NODE_ENV !== 'production') {
  globalThis.prisma = prisma
}

/**
 * Find upload by ID
 */
export async function findUploadById(id: string) {
  return await prisma.upload.findUnique({
    where: { id }
  })
}
