import { prisma } from './prisma'

export interface UploadRecord {
  id: string
  // Nullable in database; distinguish from undefined (never set)
  userId: string | null
  kind: string
  originalFilename: string
  storageKey: string
  mimeType: string | null
  sizeBytes: bigint | null
  sha256: string | null
  scannedOk: boolean
  createdAt: Date
}

export interface CreateUploadData {
  userId?: string | null
  kind: string
  originalFilename: string
  storageKey: string
  mimeType?: string | null
  sizeBytes?: bigint | null
  sha256?: string | null
  scannedOk?: boolean
}

/**
 * Insert new upload record
 */
export async function createUpload(data: CreateUploadData): Promise<UploadRecord> {
  return await prisma.upload.create({
    data: {
      userId: data.userId,
      kind: data.kind,
      originalFilename: data.originalFilename,
      storageKey: data.storageKey,
      mimeType: data.mimeType,
      sizeBytes: data.sizeBytes,
      sha256: data.sha256,
      scannedOk: data.scannedOk ?? true,
    }
  })
}

/**
 * Find upload by ID
 */
export async function findUploadById(id: string): Promise<UploadRecord | null> {
  return await prisma.upload.findUnique({
    where: { id }
  })
}

/**
 * List uploads for a user
 */
export async function listUploadsForUser(
  userId: string, 
  limit = 50, 
  offset = 0
): Promise<UploadRecord[]> {
  return await prisma.upload.findMany({
    where: { userId },
    orderBy: { createdAt: 'desc' },
    take: limit,
    skip: offset
  })
}

/**
 * Test database connection
 */
export async function testConnection(): Promise<{ ok: boolean; error?: string }> {
  try {
    await prisma.$queryRaw`SELECT 1`
    return { ok: true }
  } catch (error) {
    return { 
      ok: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }
}
