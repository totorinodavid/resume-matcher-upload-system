import { NextRequest } from 'next/server'

/**
 * Verify admin token from Authorization header
 */
export function verifyAdminToken(request: NextRequest): boolean {
  const authHeader = request.headers.get('authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return false
  }
  
  const token = authHeader.substring(7)
  const adminToken = process.env.ADMIN_TOKEN
  
  if (!adminToken) {
    console.warn('ADMIN_TOKEN not configured')
    return false
  }
  
  return token === adminToken
}
