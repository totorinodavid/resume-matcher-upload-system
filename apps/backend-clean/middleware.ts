import { NextResponse, NextRequest } from 'next/server'
import { logger, withReqId } from './lib/logger'

// In-memory token bucket (per container) - acceptable for small scale
const buckets = new Map<string, { tokens: number; updated: number }>()
const RATE = Number(process.env.RATE_LIMIT_TOKENS || 30) // per window
const WINDOW_MS = Number(process.env.RATE_LIMIT_WINDOW_MS || 60_000)

function take(ip: string): boolean {
  const now = Date.now()
  let b = buckets.get(ip)
  if (!b || now - b.updated > WINDOW_MS) {
    b = { tokens: RATE, updated: now }
  }
  if (b.tokens <= 0) {
    buckets.set(ip, b)
    return false
  }
  b.tokens -= 1
  b.updated = now
  buckets.set(ip, b)
  return true
}

export function middleware(req: NextRequest) {
  if (req.nextUrl.pathname.startsWith('/api')) {
    const ip = req.headers.get('x-forwarded-for')?.split(',')[0].trim() || 'unknown'
    const reqId = withReqId(req.headers)
    if (!take(ip)) {
      logger.warn('rate.limit', { ip, path: req.nextUrl.pathname, reqId })
      const res = NextResponse.json({ error: 'rate_limited' }, { status: 429 })
      res.headers.set('x-request-id', reqId)
      return res
    }
    const res = NextResponse.next()
    res.headers.set('x-request-id', reqId)
    return res
  }
  return NextResponse.next()
}

export const config = {
  matcher: ['/api/:path*']
}