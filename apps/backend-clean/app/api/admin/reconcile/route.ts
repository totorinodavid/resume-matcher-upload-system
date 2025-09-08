import { NextRequest, NextResponse } from 'next/server'
import { verifyAdminToken } from '../../../../lib/admin'
import { logger, withReqId } from '../../../../lib/logger'
import { prisma } from '../../../../lib/prisma'
import { promises as fs } from 'fs'
import { join } from 'path'
import { shardPath } from '../../../../lib/disk'
import { err } from '../../../../lib/errors'

export const runtime = 'nodejs'

// Depth=2 shard scan (first two shard directories) to discover files not in DB
async function* walkFiles(root: string) {
  let level1: string[] = []
  try { level1 = await fs.readdir(root) } catch { return }
  for (const a of level1) {
    const p1 = join(root, a)
    let level2: string[] = []
    try { level2 = await fs.readdir(p1) } catch { continue }
    for (const b of level2) {
      const p2 = join(p1, b)
      let files: string[] = []
      try { files = await fs.readdir(p2) } catch { continue }
      for (const f of files) {
        if (f.endsWith('.tmp')) continue
        yield join(p2, f)
      }
    }
  }
}

function extractHash(fullPath: string, filesDir: string): string | null {
  const rel = fullPath.replace(filesDir + '/', '')
  const parts = rel.split('/')
  const hash = parts[2]
  if (hash && /^[a-f0-9]{64}$/.test(hash)) return hash
  return null
}

export async function POST(request: NextRequest) {
  const reqId = withReqId(request.headers)
  if (!verifyAdminToken(request)) {
    return NextResponse.json(err('unauthorized', 'Unauthorized'), { status: 401, headers: { 'x-request-id': reqId } })
  }
  const url = new URL(request.url)
  const mode = url.searchParams.get('mode') || 'scan' // scan | delete
  const limit = Number(url.searchParams.get('limit') || 500)
  const FILES_DIR = process.env.FILES_DIR || '/var/data'
  const orphans: { hash: string }[] = []
  let scanned = 0
  for await (const fp of walkFiles(FILES_DIR)) {
    scanned++
    const hash = extractHash(fp, FILES_DIR)
    if (!hash) continue
    const exists = await prisma.upload.findUnique({ where: { sha256Hash: hash }, select: { id: true } })
    if (!exists) {
      orphans.push({ hash })
      if (orphans.length >= limit) break
    }
  }
  if (mode === 'delete' && orphans.length) {
    let deleted = 0
    for (const o of orphans) {
      try {
        await fs.unlink(shardPath(o.hash))
        deleted++
      } catch {/* ignore */}
    }
    logger.warn('admin.reconcile.delete', { reqId, deleted })
    return NextResponse.json({ mode, deleted, scanned, remainingSample: orphans.map(o => o.hash).slice(0,20) }, { headers: { 'x-request-id': reqId } })
  }
  logger.info('admin.reconcile.scan', { reqId, orphans: orphans.length, scanned })
  return NextResponse.json({ mode, scanned, orphans: orphans.map(o => o.hash) }, { headers: { 'x-request-id': reqId } })
}