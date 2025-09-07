import { NextRequest, NextResponse } from 'next/server'
import { getDiskUsage } from '@/lib/disk'
import { verifyAdminToken } from '@/lib/admin'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  if (!verifyAdminToken(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }
  
  try {
    const usage = await getDiskUsage()
    return NextResponse.json(usage)
  } catch (error) {
    return NextResponse.json({ error: 'Failed to get disk usage' }, { status: 500 })
  }
}
