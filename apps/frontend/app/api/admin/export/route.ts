import { NextRequest, NextResponse } from 'next/server'
import { requireAdmin } from '@/lib/admin'

export const runtime = 'nodejs'

export async function POST(request: NextRequest) {
  try {
    // Require admin authentication
    requireAdmin(request)
    
    // Log the export request
    const timestamp = new Date().toISOString()
    console.log('Export requested', {
      timestamp,
      requestedBy: 'admin',
      action: 'manual_export_trigger'
    })
    
    // Return accepted response - actual export implementation will be added later
    return NextResponse.json(
      {
        message: 'Export request logged successfully',
        timestamp,
        status: 'accepted'
      },
      { status: 202 }
    )
    
  } catch (error) {
    if (error instanceof Response) {
      return error
    }
    
    console.error('Admin export failed', {
      error: error instanceof Error ? error.message : 'Unknown error'
    })
    
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to process export request'
        }
      },
      { status: 500 }
    )
  }
}
