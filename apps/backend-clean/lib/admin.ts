import { NextRequest } from 'next/server'
import { createHash, timingSafeEqual } from 'crypto'
import { logger, withReqId } from './logger'

/**
 * Verify admin token from Authorization header
 */
export function verifyAdminToken(request: NextRequest): boolean {
  const reqId = withReqId(request.headers)
  const authHeader = request.headers.get('authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    logger.warn('admin.auth.missing', { reqId })
    return false
  }
  const token = authHeader.substring(7)
  const plain = process.env.ADMIN_TOKEN
  const hashed = process.env.ADMIN_TOKEN_HASH
  if (!plain && !hashed) {
    logger.warn('admin.auth.unconfigured', { reqId })
    return false
  }
  try {
    if (hashed) {
      const h = createHash('sha256').update(token).digest()
      const expected = Buffer.from(hashed, 'hex')
      if (expected.length === h.length && timingSafeEqual(expected, h)) {
        return true
      }
    }
  } catch {}
  if (plain && token.length === plain.length && timingSafeEqual(Buffer.from(token), Buffer.from(plain))) {
    return true
  }
  logger.warn('admin.auth.invalid', { reqId })
  return false
}
