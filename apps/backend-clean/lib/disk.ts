import { promises as fs } from 'fs'
import { join, dirname } from 'path'

const FILES_DIR = process.env.FILES_DIR || '/var/data'

/**
 * Create sharded path for file storage
 */
export function shardPath(hash: string): string {
  const shard1 = hash.substring(0, 2)
  const shard2 = hash.substring(2, 4)
  return join(FILES_DIR, shard1, shard2, hash)
}

/**
 * Write file to sharded storage
 */
export async function writeFile(hash: string, buffer: Buffer): Promise<string> {
  const filePath = shardPath(hash)
  const dir = dirname(filePath)
  await fs.mkdir(dir, { recursive: true })
  const tmpPath = filePath + '.tmp'
  await fs.writeFile(tmpPath, buffer)
  await fs.rename(tmpPath, filePath)
  return hash
}

export async function deleteFileIfExists(hash: string): Promise<void> {
  try {
    const filePath = shardPath(hash)
    await fs.unlink(filePath)
  } catch {
    // ignore
  }
}

/**
 * Read file from sharded storage
 */
export async function readFile(hash: string): Promise<Buffer> {
  const filePath = shardPath(hash)
  return await fs.readFile(filePath)
}

/**
 * Get disk usage statistics
 */
export async function getDiskUsage() {
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
