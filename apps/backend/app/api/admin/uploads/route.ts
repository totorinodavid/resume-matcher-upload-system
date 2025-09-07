import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { verifyAdminToken } from '@/lib/admin'

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
    const uploads = await prisma.upload.findMany({
      orderBy: { createdAt: 'desc' },
      take: 100 // Limit to last 100 uploads
    })

    const uploadList = uploads.map(upload => ({
      id: upload.id,
      filename: upload.originalFilename,
      size: upload.fileSizeBytes,
      type: upload.mimeType,
      uploadedAt: upload.createdAt,
      hash: upload.sha256Hash.substring(0, 8) // First 8 chars for display
    }))

    return NextResponse.json({
      uploads: uploadList,
      total: uploads.length
    })

  } catch (error) {
    console.error('Failed to list uploads', {
      error: error instanceof Error ? error.message : 'Unknown error'
    })
    
    return NextResponse.json(
      {
        error: {
          code: 'INTERNAL_SERVER_ERROR',
          message: 'Failed to list uploads'
        }
      },
      { status: 500 }
    )
  }
}
