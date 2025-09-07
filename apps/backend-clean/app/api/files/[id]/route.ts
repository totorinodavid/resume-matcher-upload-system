import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { readFile } from '@/lib/disk'

export const runtime = 'nodejs'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const upload = await prisma.upload.findUnique({
      where: { id: params.id }
    })
    
    if (!upload) {
      return NextResponse.json({ error: 'File not found' }, { status: 404 })
    }
    
    // Read file from storage
    const fileBuffer = await readFile(upload.storageKey)
    
    // Return file with proper headers
    return new Response(fileBuffer, {
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
