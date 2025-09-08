import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '../../../../lib/prisma'
import { verifyAdminToken } from '../../../../lib/admin'
import { logger, withReqId } from '../../../../lib/logger'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  const reqId = withReqId(request.headers)
  if (!verifyAdminToken(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: { 'x-request-id': reqId } })
  }
  try {
    const uploads = await prisma.upload.findMany({
      orderBy: { createdAt: 'desc' },
      take: 100
    })
    logger.info('admin.uploads.list', { reqId, count: uploads.length })
    return NextResponse.json({
      uploads,
      total: uploads.length
    }, { headers: { 'x-request-id': reqId } })
  } catch (error: any) {
    logger.error('admin.uploads.error', { reqId, error: error?.message })
    return NextResponse.json({ error: 'Failed to fetch uploads' }, { status: 500, headers: { 'x-request-id': reqId } })
  }
}
