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
 * Generate sharded path from hash and filename
 * Uses first 4 hex chars for sharding: aa/bb/
 */
export function shardPath(hash: string, original: string): string {
  const dirA = hash.substring(0, 2)
  const dirB = hash.substring(2, 4)
  const safeOriginal = safeName(original)
  const filename = `${hash}__${safeOriginal}`
  
  return `disk://uploads/${dirA}/${dirB}/${filename}`
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
  storageKey: string, 
  source: Buffer | Readable
): Promise<void> {
  const absolutePath = pathFromStorageKey(storageKey)
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
 * Get file path from storage key
 */
export function pathFromStorageKey(storageKey: string): string {
  return path.join(BASE_DIR, storageKey)
}

/**
 * Get disk usage statistics
 */
export async function diskUsage(): Promise<{
  total: number
  used: number
  available: number
}> {
  try {
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
    
    const used = await getDirSize(BASE_DIR)
    
    // For mounted disks, we'll estimate total space
    // In production, this would come from statvfs or similar
    const total = 10 * 1024 * 1024 * 1024 // 10GB
    const available = total - used
    
    return {
      total,
      used,
      available
    }
  } catch (error) {
    throw new Error(`Failed to get disk usage: ${error}`)
  }
}
