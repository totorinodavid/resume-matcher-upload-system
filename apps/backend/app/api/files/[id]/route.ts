import { NextRequest, NextResponse } from 'next/server'
import { createReadStream, promises as fs } from 'fs'
import { prisma } from '@/lib/prisma'
import { pathFromStorageKey } from '@/lib/disk'

export const runtime = 'nodejs'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    
    // Find upload record in database
    const upload = await prisma.upload.findUnique({
      where: { id }
    })
    
    if (!upload) {
      return NextResponse.json(
        {
          error: {
            code: 'NOT_FOUND',
            message: 'File not found'
          }
        },
        { status: 404 }
      )
    }

    // Get absolute file path
    const filePath = pathFromStorageKey(upload.storageKey)
    
    // Check if file exists on disk
    try {
      await fs.access(filePath)
    } catch {
      return NextResponse.json(
        {
          error: {
            code: 'FILE_NOT_FOUND',
            message: 'File not found on disk'
          }
        },
        { status: 404 }
      )
    }

    // Get file stats
    const stats = await fs.stat(filePath)
    
    // Set appropriate headers
    const headers = new Headers()
    headers.set('Content-Type', upload.mimeType || 'application/octet-stream')
    headers.set('Content-Length', stats.size.toString())
    headers.set('Content-Disposition', `attachment; filename="${upload.originalFilename}"`)
    headers.set('Cache-Control', 'private, max-age=3600')
    
    // Create readable stream
    const fileStream = createReadStream(filePath)
    
    // Convert Node.js stream to Web API ReadableStream
    const webStream = new ReadableStream({
      start(controller) {
        fileStream.on('data', (chunk) => {
          controller.enqueue(new Uint8Array(chunk))
        })
        fileStream.on('end', () => {
          controller.close()
        })
        fileStream.on('error', (error) => {
          controller.error(error)
        })
      },
      cancel() {
        fileStream.destroy()
      }
    })

    return new Response(webStream, {
      status: 200,
      headers
    })

  } catch (error) {
    console.error('File download failed', {
      fileId: params.id,
      error: error instanceof Error ? error.message : 'Unknown error'
    })
    
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to download file'
        }
      },
      { status: 500 }
    )
  }
}
