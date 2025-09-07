import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '../../../../lib/prisma'
import { verifyAdminToken } from '../../../../lib/admin'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  if (!verifyAdminToken(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  try {
    const uploads = await prisma.upload.findMany({
      orderBy: { createdAt: 'desc' },
      take: 100
    })
    
    return NextResponse.json({
      uploads,
      total: uploads.length
    })
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch uploads' }, { status: 500 })
  }
}
