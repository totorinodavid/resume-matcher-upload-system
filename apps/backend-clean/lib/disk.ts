import { promises as fs } from 'fs'
import { join, dirname } from 'path'
import { prisma } from './prisma'
import { createReadStream, createWriteStream } from 'fs'
import { createHash } from 'crypto'

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

/**
 * Stream a File (web File object) to temp file while computing SHA-256.
 * Enforces size limit. Returns hash and final size. Does NOT move into sharded
 * location automatically; caller should perform dedupe check then finalize via rename.
 */
export async function streamAndHashFile(file: File, maxBytes: number) : Promise<{
  hash: string; size: number; tmpPath: string; finalize: (hash: string) => Promise<string>; discard: () => Promise<void>;
}> {
  const hash = createHash('sha256')
  let size = 0
  const tmpPath = join(FILES_DIR, `.tmp-${Date.now()}-${Math.random().toString(36).slice(2)}`)
  await fs.mkdir(dirname(tmpPath), { recursive: true })
  const ws = createWriteStream(tmpPath)
  const reader = file.stream().getReader()
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      if (!value) continue
      const buf = Buffer.from(value)
      size += buf.length
      if (size > maxBytes) {
        ws.destroy()
        throw new Error('too_large')
      }
      hash.update(buf)
      if (!ws.write(buf)) {
        await new Promise<void>(resolve => ws.once('drain', () => resolve()))
      }
    }
  } catch (e) {
    try { ws.destroy() } catch {}
    try { await fs.unlink(tmpPath) } catch {}
    throw e
  }
  await new Promise(res => ws.end(res))
  const digest = hash.digest('hex')
  async function finalize(finalHash: string) {
    const finalPath = shardPath(finalHash)
    await fs.mkdir(dirname(finalPath), { recursive: true })
    await fs.rename(tmpPath, finalPath)
    return finalHash
  }
  async function discard() {
    try { await fs.unlink(tmpPath) } catch {}
  }
  return { hash: digest, size, tmpPath, finalize, discard }
}

export async function deleteFileIfExists(hash: string): Promise<void> {
  try {
    const filePath = shardPath(hash)
    await fs.unlink(filePath)
  } catch {
    // ignore
  }
}

export function createFileReadStream(hash: string) {
  const filePath = shardPath(hash)
  return createReadStream(filePath)
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
  const TOTAL = parseInt(process.env.DISK_TOTAL_BYTES || '') || 10 * 1024 * 1024 * 1024
  try {
    // Use DB aggregates instead of filesystem crawling (O(1) vs O(N))
    const agg = await prisma.upload.aggregate({
      _sum: { fileSizeBytes: true },
      _count: { _all: true }
    })
    const used = agg._sum.fileSizeBytes || 0
    return {
      mode: 'db-aggregate',
      used,
      available: Math.max(TOTAL - used, 0),
      total: TOTAL,
      files: agg._count._all
    }
  } catch (e) {
    // Fallback to lightweight existence check (not deep scan)
    try {
      await fs.access(FILES_DIR)
    } catch {
      // directory missing
      return { mode: 'error', used: 0, available: TOTAL, total: TOTAL, files: 0 }
    }
    return { mode: 'error-db', used: 0, available: TOTAL, total: TOTAL, files: 0 }
  }
}

// Lightweight write test for health endpoint
export async function testWriteLatency(): Promise<{ ok: boolean; latencyMs: number }> {
  const start = performance.now()
  const probeDir = join(FILES_DIR, '.health')
  const probeFile = join(probeDir, 'probe.txt')
  try {
    await fs.mkdir(probeDir, { recursive: true })
    await fs.writeFile(probeFile, Date.now().toString())
    await fs.readFile(probeFile)
    await fs.unlink(probeFile).catch(() => {})
    return { ok: true, latencyMs: +(performance.now() - start).toFixed(2) }
  } catch {
    return { ok: false, latencyMs: +(performance.now() - start).toFixed(2) }
  }
}
