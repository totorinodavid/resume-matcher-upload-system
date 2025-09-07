/**
 * Read Bearer token from Authorization header
 */
export function readBearerToken(request: Request): string | null {
  const authHeader = request.headers.get('authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null
  }
  return authHeader.slice(7) // Remove 'Bearer ' prefix
}

/**
 * Require admin authentication
 * Throws 401 if not authenticated
 */
export function requireAdmin(request: Request): void {
  const token = readBearerToken(request)
  const adminToken = process.env.ADMIN_TOKEN
  
  if (!adminToken) {
    throw new Error('ADMIN_TOKEN environment variable not set')
  }
  
  if (!token || token !== adminToken) {
    throw new Response(
      JSON.stringify({
        error: {
          code: 'UNAUTHORIZED',
          message: 'Valid admin token required'
        }
      }),
      { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
}
