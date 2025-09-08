import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '../../../../lib/prisma'
import { createFileReadStream } from '../../../../lib/disk'
import { statSync } from 'fs'
import { logger, withReqId } from '../../../../lib/logger'
import { err } from '../../../../lib/errors'

export const runtime = 'nodejs'

// NOTE: Next.js 15 route type generation currently widens dynamic route params to a Promise in the
// emitted type declarations (.next/types/...). To stay compatible (and avoid brittle generic
// constraints) we accept a generic `context` and `await` its `params` field if it's a Promise.
// This keeps runtime semantics identical while satisfying the generated validator types.
// Loosen the context type to appease generated validator types while keeping runtime robust.
export async function GET(
  request: NextRequest,
  // Using 'any' to sidestep mismatch where generated types expect Promise-wrapped params.
  context: any
) {
  const rawParams = context?.params
  const paramsObj = rawParams && typeof rawParams.then === 'function' ? await rawParams : rawParams
  const { id } = (paramsObj || { id: '' }) as { id: string }
  const reqId = withReqId(request.headers)
  try {
    const upload = await prisma.upload.findUnique({
      where: { id }
    })

    if (!upload) {
      logger.info('file.not_found', { reqId, id })
  return NextResponse.json(err('not_found', 'File not found'), { status: 404, headers: { 'x-request-id': reqId } })
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
  return NextResponse.json(err('blob_missing', 'File blob missing'), { status: 410, headers: { 'x-request-id': reqId } })
    }
  } catch (error: any) {
    logger.error('file.download.error', { reqId, error: error?.message })
  return NextResponse.json(err('download_failed', 'Download failed'), { status: 500, headers: { 'x-request-id': reqId } })
  }
}
