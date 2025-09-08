import { NextResponse } from 'next/server'
import { prisma } from '../../../lib/prisma'
import { getDiskUsage, testWriteLatency } from '../../../lib/disk'

export const runtime = 'nodejs'

export async function GET() {
  try {
    const started = performance.now()
    await prisma.$queryRaw`SELECT 1`
    const dbLatency = +(performance.now() - started).toFixed(2)
    const disk = await getDiskUsage()
    const diskProbe = await testWriteLatency()
    const mem = process.memoryUsage()
    return NextResponse.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      service: 'upload-system',
      version: '1.0.0',
      database: { state: 'connected', latencyMs: dbLatency },
      disk: { ...disk, writeTest: diskProbe },
      memory: {
        rss: mem.rss,
        heapUsed: mem.heapUsed,
        heapTotal: mem.heapTotal,
        external: mem.external
      }
    })
  } catch (error) {
    console.error('Health check failed:', error)
    return NextResponse.json({
      status: 'unhealthy',
      timestamp: new Date().toISOString(),
      database: 'disconnected',
      error: error instanceof Error ? error.message : 'Database connection failed'
    }, { status: 503 })
  }
}
