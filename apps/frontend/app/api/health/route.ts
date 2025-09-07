import { NextResponse } from 'next/server'
import { testConnection } from '@/lib/db'

export const runtime = 'nodejs'

export async function GET() {
  try {
    // Test database connection
    const dbCheck = await testConnection()
    
    if (!dbCheck.ok) {
      return NextResponse.json(
        {
          ok: false,
          database: dbCheck,
          timestamp: new Date().toISOString()
        },
        { status: 503 }
      )
    }
    
    return NextResponse.json(
      {
        ok: true,
        database: { ok: true },
        timestamp: new Date().toISOString()
      },
      { status: 200 }
    )
    
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}
