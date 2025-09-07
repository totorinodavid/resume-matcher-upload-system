import { NextRequest, NextResponse } from 'next/server'
import { diskUsage } from '../../../../lib/disk-simple'
import { verifyAdminToken } from '../../../../lib/admin'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  // Verify admin authentication
  const authResult = await verifyAdminToken(request)
  if (!authResult.success) {
    return NextResponse.json(
      {
        error: {
          code: 'UNAUTHORIZED',
          message: 'Admin authentication required'
        }
      },
      { status: 401 }
    )
  }

  try {
    const usage = await diskUsage()
    
    return NextResponse.json({
      disk: {
        total: usage.total,
        used: usage.used,
        available: usage.available,
        usagePercent: Math.round((usage.used / usage.total) * 100)
      }
    })

  } catch (error) {
    console.error('Failed to get disk usage', {
      error: error instanceof Error ? error.message : 'Unknown error'
    })
    
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to get disk usage'
        }
      },
      { status: 500 }
    )
  }
}
