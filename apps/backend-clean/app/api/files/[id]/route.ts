import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '../../../../lib/prisma'
import { readFile } from '../../../../lib/disk'

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
    let fileBuffer: Buffer
    try {
      fileBuffer = await readFile(upload.storageKey)
    } catch {
      return NextResponse.json({ error: 'File blob missing' }, { status: 410 })
    }
    
    // Return file with proper headers
    return new Response(new Uint8Array(fileBuffer), {
      headers: {
        'Content-Type': upload.mimeType,
        'Content-Length': upload.fileSizeBytes.toString(),
        'Content-Disposition': `attachment; filename="${upload.originalFilename}"`,
        'Cache-Control': 'public, max-age=31536000, immutable'
      }
    })
    
  } catch (error) {
    console.error('Download error:', error)
    return NextResponse.json({ error: 'Download failed' }, { status: 500 })
  }
}
