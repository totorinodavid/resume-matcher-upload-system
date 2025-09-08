import { NextRequest } from 'next/server'

/**
 * Read Bearer token from Authorization header
 */
export function readBearerToken(request: NextRequest): string | null {
  const authHeader = request.headers.get('authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null
  }
  return authHeader.slice(7) // Remove 'Bearer ' prefix
}

/**
 * Verify admin authentication
 */
export async function verifyAdminToken(request: NextRequest): Promise<{
  success: boolean
  error?: string
}> {
  const token = readBearerToken(request)
  const adminToken = process.env.ADMIN_TOKEN
  
  if (!adminToken) {
    return {
      success: false,
      error: 'ADMIN_TOKEN environment variable not set'
    }
  }
  
  if (!token || token !== adminToken) {
    return {
      success: false,
      error: 'Invalid or missing admin token'
    }
  }
  
  return { success: true }
}
