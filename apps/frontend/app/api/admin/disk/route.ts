import { NextRequest, NextResponse } from 'next/server'
import { requireAdmin } from '@/lib/admin'
import { diskUsage } from '@/lib/disk'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  try {
    // Require admin authentication
    requireAdmin(request)
    
    // Get disk usage statistics
    const usage = await diskUsage()
    
    return NextResponse.json(usage, { status: 200 })
    
  } catch (error) {
    if (error instanceof Response) {
      return error
    }
    
    console.error('Admin disk check failed', {
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
