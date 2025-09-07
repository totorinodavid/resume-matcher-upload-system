import { NextRequest, NextResponse } from 'next/server'
import { promises as fs } from 'fs'
import { createHash } from 'crypto'
import { prisma } from '../../../lib/prisma'
import { shardPath, writeFileStream } from '../../../lib/disk'

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
      return NextResponse.json(
        {
          error: {
            code: 'NO_FILE',
            message: 'No file provided'
          }
        },
        { status: 400 }
      )
    }

    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_FILE_TYPE',
            message: 'Only PDF and DOCX files are allowed'
          }
        },
        { status: 400 }
      )
    }

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        {
          error: {
            code: 'FILE_TOO_LARGE',
            message: 'File size must be less than 10MB'
          }
        },
        { status: 400 }
      )
    }

    // Generate file hash
    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)
    const hash = createHash('sha256').update(buffer).digest('hex')
    
    // Check for duplicates
    const existingUpload = await prisma.upload.findUnique({
      where: { sha256Hash: hash }
    })
    
    if (existingUpload) {
      return NextResponse.json(
        {
          upload: {
            id: existingUpload.id,
            filename: existingUpload.originalFilename,
            size: existingUpload.fileSizeBytes,
            uploadedAt: existingUpload.createdAt,
            duplicate: true
          }
        },
        { status: 200 }
      )
    }

    // Generate storage path
    const storageKey = shardPath(hash, file.name)
    
    // Write file to disk
    await writeFileStream(storageKey, buffer)
    
    // Save metadata to database
    const upload = await prisma.upload.create({
      data: {
        originalFilename: file.name,
        mimeType: file.type,
        fileSizeBytes: file.size,
        sha256Hash: hash,
        storageKey: storageKey,
        metadata: {
          uploadedFrom: 'web',
          userAgent: request.headers.get('user-agent') || 'unknown'
        }
      }
    })

    return NextResponse.json(
      {
        upload: {
          id: upload.id,
          filename: upload.originalFilename,
          size: upload.fileSizeBytes,
          uploadedAt: upload.createdAt,
          duplicate: false
        }
      },
      { status: 201 }
    )

  } catch (error) {
    console.error('File upload failed', {
      error: error instanceof Error ? error.message : 'Unknown error'
    })
    
    return NextResponse.json(
      {
        error: {
          code: 'UPLOAD_FAILED',
          message: 'Failed to upload file'
        }
      },
      { status: 500 }
    )
  }
}
