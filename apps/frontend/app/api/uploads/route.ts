import { NextRequest, NextResponse } from 'next/server'
import { createHash } from 'crypto'
import { shardPath, writeFileStream } from '@/lib/disk'
import { createUpload } from '@/lib/db'

export const runtime = 'nodejs'

const MAX_UPLOAD_MB = parseInt(process.env.MAX_UPLOAD_MB ?? '20')
const MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]

const ALLOWED_KINDS = ['resume', 'job_posting', 'optimized', 'other']

function generateRequestId(): string {
  return Math.random().toString(36).substring(2, 15)
}

async function streamToBuffer(stream: ReadableStream): Promise<Buffer> {
  const chunks: Uint8Array[] = []
  const reader = stream.getReader()
  
  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      chunks.push(value)
    }
  } finally {
    reader.releaseLock()
  }
  
  const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0)
  const buffer = Buffer.allocUnsafe(totalLength)
  let offset = 0
  
  for (const chunk of chunks) {
    buffer.set(chunk, offset)
    offset += chunk.length
  }
  
  return buffer
}

export async function POST(request: NextRequest) {
  const requestId = generateRequestId()
  
  try {
    const contentType = request.headers.get('content-type')
    if (!contentType?.startsWith('multipart/form-data')) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_CONTENT_TYPE',
            message: 'Content-Type must be multipart/form-data'
          },
          requestId
        },
        { status: 400 }
      )
    }

    const formData = await request.formData()
    const file = formData.get('file') as File | null
    
    if (!file) {
      return NextResponse.json(
        {
          error: {
            code: 'MISSING_FILE',
            message: 'File field is required'
          },
          requestId
        },
        { status: 400 }
      )
    }

    // Validate file size
    if (file.size > MAX_UPLOAD_BYTES) {
      return NextResponse.json(
        {
          error: {
            code: 'FILE_TOO_LARGE',
            message: `File size exceeds ${MAX_UPLOAD_MB}MB limit`
          },
          requestId
        },
        { status: 413 }
      )
    }

    // Validate MIME type
    if (!ALLOWED_MIME_TYPES.includes(file.type)) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_MIME_TYPE',
            message: `File type ${file.type} not allowed. Allowed types: ${ALLOWED_MIME_TYPES.join(', ')}`
          },
          requestId
        },
        { status: 415 }
      )
    }

    // Get optional fields
    const userId = formData.get('userId') as string | null
    const kind = (formData.get('kind') as string) ?? 'other'
    
    // Validate kind
    if (!ALLOWED_KINDS.includes(kind)) {
      return NextResponse.json(
        {
          error: {
            code: 'INVALID_KIND',
            message: `Invalid kind. Allowed values: ${ALLOWED_KINDS.join(', ')}`
          },
          requestId
        },
        { status: 400 }
      )
    }

    // Generate UUID for this upload
    const uploadId = crypto.randomUUID()
    
    // Read file content and calculate SHA256
    const fileBuffer = await streamToBuffer(file.stream())
    const sha256 = createHash('sha256').update(fileBuffer).digest('hex')
    
    // Generate storage path
    const { rel: relativePath, abs: absolutePath } = shardPath(uploadId, file.name)
    const storageKey = `disk://${relativePath}`
    
    // Write file to disk
    await writeFileStream(absolutePath, fileBuffer)
    
    // Save metadata to database
    const uploadRecord = await createUpload({
      userId: userId || undefined,
      kind,
      originalFilename: file.name,
      storageKey,
      mimeType: file.type,
      sizeBytes: BigInt(file.size),
      sha256,
      scannedOk: true
    })

    console.log('Upload successful', {
      uploadId: uploadRecord.id,
      originalFilename: file.name,
      sizeBytes: file.size,
      mimeType: file.type,
      userId,
      kind,
      requestId
    })

    return NextResponse.json(
      {
        uploadId: uploadRecord.id,
        storageKey,
        sizeBytes: file.size,
        sha256
      },
      { status: 201 }
    )

  } catch (error) {
    console.error('Upload failed', {
      error: error instanceof Error ? error.message : 'Unknown error',
      requestId
    })
    
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Upload failed due to server error'
        },
        requestId
      },
      { status: 500 }
    )
  }
}
