import { NextRequest, NextResponse } from 'next/server'
import { createHash } from 'crypto'
import { prisma } from '../../../lib/prisma'
import { writeFile } from '../../../lib/disk'

export const runtime = 'nodejs'

const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/msword'
]

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }
    
    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return NextResponse.json({ error: 'File type not allowed' }, { status: 400 })
    }
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json({ error: 'File too large' }, { status: 400 })
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
      return NextResponse.json({
        id: existing.id,
        message: 'File already exists',
        duplicate: true
      })
    }
    
    // Store file
    const storageKey = await writeFile(hash, buffer)
    
    // Save to database
    const upload = await prisma.upload.create({
      data: {
        originalFilename: file.name,
        mimeType: file.type,
        fileSizeBytes: file.size,
        sha256Hash: hash,
        storageKey,
        metadata: {
          userAgent: request.headers.get('user-agent'),
          uploadedAt: new Date().toISOString()
        }
      }
    })
    
    return NextResponse.json({
      id: upload.id,
      filename: upload.originalFilename,
      size: upload.fileSizeBytes,
      hash: upload.sha256Hash,
      created: upload.createdAt
    })
    
  } catch (error) {
    console.error('Upload error:', error)
    return NextResponse.json({ error: 'Upload failed' }, { status: 500 })
  }
}
