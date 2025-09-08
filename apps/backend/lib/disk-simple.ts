import { promises as fs } from 'fs'
import { join } from 'path'

const FILES_DIR = process.env.FILES_DIR || './uploads'

/**
 * Create sharded path for file storage
 */
export function shardPath(filename: string): string {
  const shard1 = filename[0] || '0'
  const shard2 = filename[1] || '0'
  return join(FILES_DIR, shard1, shard2, filename)
}

/**
 * Write file stream to disk
 */
export async function writeFileStream(filename: string, buffer: Buffer): Promise<string> {
  const filePath = shardPath(filename)
  const dir = join(filePath, '..')
  
  await fs.mkdir(dir, { recursive: true })
  await fs.writeFile(filePath, buffer)
  
  return filePath
}

/**
 * Get file path from storage key
 */
export function pathFromStorageKey(storageKey: string): string {
  return join(FILES_DIR, storageKey)
}

/**
 * Get disk usage statistics
 */
export async function diskUsage(): Promise<{
  used: number
  available: number
  total: number
  files: number
}> {
  try {
    const files = await getAllFiles(FILES_DIR)
    
    let totalSize = 0
    for (const file of files) {
      try {
        const stats = await fs.stat(file)
        totalSize += stats.size
      } catch {
        continue
      }
    }
    
    return {
      used: totalSize,
      available: 10 * 1024 * 1024 * 1024 - totalSize,
      total: 10 * 1024 * 1024 * 1024,
      files: files.length
    }
  } catch {
    return {
      used: 0,
      available: 10 * 1024 * 1024 * 1024,
      total: 10 * 1024 * 1024 * 1024,
      files: 0
    }
  }
}

async function getAllFiles(dir: string): Promise<string[]> {
  try {
    const entries = await fs.readdir(dir, { withFileTypes: true })
    const files: string[] = []
    
    for (const entry of entries) {
      const fullPath = join(dir, entry.name)
      if (entry.isDirectory()) {
        files.push(...await getAllFiles(fullPath))
      } else {
        files.push(fullPath)
      }
    }
    
    return files
  } catch {
    return []
  }
}
