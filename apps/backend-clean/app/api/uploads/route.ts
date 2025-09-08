import { NextRequest, NextResponse } from 'next/server'
import { createHash } from 'crypto'
import { prisma } from '../../../lib/prisma'
import { writeFile, deleteFileIfExists } from '../../../lib/disk'
import { logger, withReqId } from '../../../lib/logger'
import { err } from '../../../lib/errors'

export const runtime = 'nodejs'

const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword'
]

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export async function POST(request: NextRequest) {
  try {
  const reqId = withReqId(request.headers)
  const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
  logger.warn('upload.missing_file', { reqId })
  return NextResponse.json(err('no_file', 'No file provided'), { status: 400, headers: { 'x-request-id': reqId } })
    }
    
    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
  logger.warn('upload.type_blocked', { reqId, type: file.type })
  return NextResponse.json(err('type_blocked', 'File type not allowed'), { status: 400, headers: { 'x-request-id': reqId } })
    }
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
  logger.warn('upload.too_large', { reqId, size: file.size })
  return NextResponse.json(err('too_large', 'File too large'), { status: 400, headers: { 'x-request-id': reqId } })
    }
    
    // Read file data
    const buffer = Buffer.from(await file.arrayBuffer())
    
    // Generate SHA256 hash
    const hash = createHash('sha256').update(buffer).digest('hex')
    
    // Check for duplicate
    const existing = await prisma.upload.findUnique({
      where: { sha256Hash: hash }
    })
    
    if (existing) {
      logger.info('upload.duplicate.fastpath', { reqId, id: existing.id })
      return NextResponse.json({
        id: existing.id,
        message: 'File already exists',
        duplicate: true
      }, { headers: { 'x-request-id': reqId } })
    }
    
    // Store file atomically
    await writeFile(hash, buffer)
    try {
      const upload = await prisma.upload.create({
        data: {
          originalFilename: file.name,
          mimeType: file.type,
          fileSizeBytes: file.size,
          sha256Hash: hash,
          storageKey: hash,
          metadata: {
            userAgent: request.headers.get('user-agent'),
            uploadedAt: new Date().toISOString()
          }
        }
      })
      logger.info('upload.success', { reqId, id: upload.id, size: upload.fileSizeBytes })
      return NextResponse.json({
        id: upload.id,
        filename: upload.originalFilename,
        size: upload.fileSizeBytes,
        hash: upload.sha256Hash,
        created: upload.createdAt
      }, { headers: { 'x-request-id': reqId } })
    } catch (e: any) {
      // Unique constraint (duplicate race)
      if (e?.code === 'P2002') {
        const existing = await prisma.upload.findUnique({ where: { sha256Hash: hash } })
        if (existing) {
          logger.info('upload.duplicate.race', { reqId, id: existing.id })
          return NextResponse.json({
            id: existing.id,
            message: 'File already exists',
            duplicate: true
          }, { headers: { 'x-request-id': reqId } })
        }
      }
      // Rollback orphaned file if DB failed for other reasons
      await deleteFileIfExists(hash)
  logger.error('upload.db_error', { reqId, error: e?.code || 'unknown' })
  throw e
    }
    
  } catch (error) {
    const reqId = withReqId(request.headers)
    logger.error('upload.unhandled', { reqId, error: (error as any)?.message })
  return NextResponse.json(err('upload_failed', 'Upload failed'), { status: 500, headers: { 'x-request-id': reqId } })
  }
}
