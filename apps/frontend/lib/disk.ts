import { promises as fs } from 'fs'
import path from 'path'
import { createHash } from 'crypto'
import { Readable } from 'stream'
import { pipeline } from 'stream/promises'

export const BASE_DIR = process.env.FILES_DIR ?? '/var/data'

/**
 * Sanitize filename to only allow safe characters
 */
export function safeName(original: string): string {
  return original.replace(/[^a-zA-Z0-9._-]/g, '_')
}

/**
 * Generate sharded path from UUID and filename
 * Uses first 4 hex chars of SHA1 hash for sharding: aa/bb/
 */
export function shardPath(id: string, original: string): { rel: string; abs: string } {
  const hash = createHash('sha1').update(id).digest('hex')
  const dirA = hash.substring(0, 2)
  const dirB = hash.substring(2, 4)
  const safeOriginal = safeName(original)
  const filename = `${id}__${safeOriginal}`
  
  const rel = path.posix.join('uploads', dirA, dirB, filename)
  const abs = path.join(BASE_DIR, rel)
  
  return { rel, abs }
}

/**
 * Ensure directory exists
 */
export async function ensureDir(dir: string): Promise<void> {
  try {
    await fs.mkdir(dir, { recursive: true })
  } catch (error) {
    // Ignore if directory already exists
    if ((error as NodeJS.ErrnoException).code !== 'EEXIST') {
      throw error
    }
  }
}

/**
 * Write file using streaming to avoid large memory usage
 */
export async function writeFileStream(
  absolutePath: string, 
  source: Buffer | Readable
): Promise<void> {
  const dir = path.dirname(absolutePath)
  await ensureDir(dir)
  
  if (Buffer.isBuffer(source)) {
    await fs.writeFile(absolutePath, source)
  } else {
    const writeStream = (await import('fs')).createWriteStream(absolutePath)
    await pipeline(source, writeStream)
  }
}

/**
 * Convert storage key to absolute path
 */
export function pathFromStorageKey(storageKey: string): string {
  if (!storageKey.startsWith('disk://')) {
    throw new Error(`Invalid storage key format: ${storageKey}`)
  }
  
  const relativePath = storageKey.slice(7) // Remove 'disk://'
  return path.join(BASE_DIR, relativePath)
}

/**
 * Get disk usage statistics
 */
export async function diskUsage(): Promise<{
  usedPercent: number
  totalBytes: number
  usedBytes: number
  baseDir: string
}> {
  try {
    const stats = await fs.stat(BASE_DIR)
    
    // Get directory size recursively
    async function getDirSize(dirPath: string): Promise<number> {
      let size = 0
      try {
        const items = await fs.readdir(dirPath, { withFileTypes: true })
        for (const item of items) {
          const itemPath = path.join(dirPath, item.name)
          if (item.isDirectory()) {
            size += await getDirSize(itemPath)
          } else {
            const itemStats = await fs.stat(itemPath)
            size += itemStats.size
          }
        }
      } catch {
        // Ignore errors for inaccessible directories
      }
      return size
    }
    
    const usedBytes = await getDirSize(BASE_DIR)
    
    // For mounted disks, we'll estimate total space
    // In production, this would come from statvfs or similar
    const totalBytes = 10 * 1024 * 1024 * 1024 // 10GB default
    const usedPercent = Math.round((usedBytes / totalBytes) * 100)
    
    return {
      usedPercent,
      totalBytes,
      usedBytes,
      baseDir: BASE_DIR
    }
  } catch (error) {
    throw new Error(`Failed to get disk usage: ${error}`)
  }
}
