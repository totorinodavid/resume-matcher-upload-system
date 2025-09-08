import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '../../../../lib/prisma'
import { readFile, createFileReadStream } from '../../../../lib/disk'
import { statSync } from 'fs'
import { logger, withReqId } from '../../../../lib/logger'

export const runtime = 'nodejs'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const reqId = withReqId(request.headers)
  try {
    const { id } = params
    const upload = await prisma.upload.findUnique({
      where: { id }
    })

    if (!upload) {
      logger.info('file.not_found', { reqId, id })
      return NextResponse.json({ error: 'File not found' }, { status: 404, headers: { 'x-request-id': reqId } })
    }

    const etag = `"${upload.sha256Hash}"`
    const ifNoneMatch = request.headers.get('if-none-match')
    if (ifNoneMatch && ifNoneMatch === etag) {
      logger.info('file.not_modified', { reqId, id })
      return new Response(null, { status: 304, headers: { 'ETag': etag, 'x-request-id': reqId } })
    }

    try {
      let contentLength = upload.fileSizeBytes.toString()
      try {
        const fsStat = statSync(require('path').join(process.env.FILES_DIR || '/var/data', upload.sha256Hash.substring(0,2), upload.sha256Hash.substring(2,4), upload.sha256Hash))
        contentLength = fsStat.size.toString()
      } catch { /* ignore */ }

      const stream = createFileReadStream(upload.storageKey)
      logger.info('file.stream.start', { reqId, id, size: contentLength, mime: upload.mimeType })
      const body = new ReadableStream({
        start(controller) {
          stream.on('data', (chunk) => controller.enqueue(chunk))
          stream.on('end', () => {
            logger.info('file.stream.end', { reqId, id })
            controller.close()
          })
          stream.on('error', (err) => {
            logger.error('file.stream.error', { reqId, id, error: err?.message })
            controller.error(err)
          })
        }
      })
      return new Response(body, {
        headers: {
          'Content-Type': upload.mimeType,
          'Content-Length': contentLength,
          'Content-Disposition': `attachment; filename="${encodeURIComponent(upload.originalFilename)}"`,
          'Cache-Control': 'public, max-age=31536000, immutable',
          'ETag': etag,
          'x-request-id': reqId
        }
      })
    } catch (e: any) {
      logger.warn('file.blob_missing', { reqId, id, error: e?.message })
      return NextResponse.json({ error: 'File blob missing' }, { status: 410, headers: { 'x-request-id': reqId } })
    }
  } catch (error: any) {
    logger.error('file.download.error', { reqId, error: error?.message })
    return NextResponse.json({ error: 'Download failed' }, { status: 500, headers: { 'x-request-id': reqId } })
  }
}
