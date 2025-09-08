import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '../../../../lib/prisma'
import { readFile, createFileReadStream } from '../../../../lib/disk'
import { statSync } from 'fs'

export const runtime = 'nodejs'

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params
    const upload = await prisma.upload.findUnique({
      where: { id }
    })
    
    if (!upload) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 })
    }
    
    // Read file from storage
    // Compute ETag using hash (already unique)
    const etag = `"${upload.sha256Hash}"`
    const ifNoneMatch = _request.headers.get('if-none-match')
    if (ifNoneMatch && ifNoneMatch === etag) {
      return new Response(null, { status: 304, headers: { 'ETag': etag } })
    }

    // Stream file
    try {
      // Attempt stat for length verification (optional vs DB size)
      let contentLength = upload.fileSizeBytes.toString()
      try {
        const fsStat = statSync(require('path').join(process.env.FILES_DIR || '/var/data', upload.sha256Hash.substring(0,2), upload.sha256Hash.substring(2,4), upload.sha256Hash))
        contentLength = fsStat.size.toString()
      } catch { /* ignore */ }

      const stream = createFileReadStream(upload.storageKey)
      const body = new ReadableStream({
        start(controller) {
          stream.on('data', (chunk) => controller.enqueue(chunk))
          stream.on('end', () => controller.close())
          stream.on('error', (err) => {
            console.error('Stream error:', err)
            controller.error(err)
          })
        }
      })
      return new Response(body, {
        headers: {
          'Content-Type': upload.mimeType,
          'Content-Length': contentLength,
          'Content-Disposition': `attachment; filename="${upload.originalFilename}"`,
          'Cache-Control': 'public, max-age=31536000, immutable',
          'ETag': etag
        }
      })
    } catch {
      return NextResponse.json({ error: 'File blob missing' }, { status: 410 })
    }
    
  } catch (error) {
    console.error('Download error:', error)
    return NextResponse.json({ error: 'Download failed' }, { status: 500 })
  }
}
