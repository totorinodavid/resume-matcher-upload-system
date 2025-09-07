import { readBearerToken, requireAdmin } from '../lib/admin'

describe('Admin Utilities', () => {
  describe('readBearerToken', () => {
    it('should extract token from valid Bearer header', () => {
      const request = new Request('http://test.com', {
        headers: {
          'authorization': 'Bearer test-token-123'
        }
      })
      
      expect(readBearerToken(request)).toBe('test-token-123')
    })

    it('should return null for missing authorization header', () => {
      const request = new Request('http://test.com')
      expect(readBearerToken(request)).toBeNull()
    })

    it('should return null for non-Bearer authorization', () => {
      const request = new Request('http://test.com', {
        headers: {
          'authorization': 'Basic dGVzdDp0ZXN0'
        }
      })
      
      expect(readBearerToken(request)).toBeNull()
    })

    it('should handle empty Bearer token', () => {
      const request = new Request('http://test.com', {
        headers: {
          'authorization': 'Bearer '
        }
      })
      
      expect(readBearerToken(request)).toBe('')
    })
  })

  describe('requireAdmin', () => {
    const originalEnv = process.env.ADMIN_TOKEN

    beforeEach(() => {
      process.env.ADMIN_TOKEN = 'test-admin-token'
    })

    afterEach(() => {
      process.env.ADMIN_TOKEN = originalEnv
    })

    it('should pass with valid admin token', () => {
      const request = new Request('http://test.com', {
        headers: {
          'authorization': 'Bearer test-admin-token'
        }
      })
      
      expect(() => requireAdmin(request)).not.toThrow()
    })

    it('should throw with invalid token', () => {
      const request = new Request('http://test.com', {
        headers: {
          'authorization': 'Bearer wrong-token'
        }
      })
      
      expect(() => requireAdmin(request)).toThrow()
    })

    it('should throw with missing authorization header', () => {
      const request = new Request('http://test.com')
      
      expect(() => requireAdmin(request)).toThrow()
    })

    it('should throw when ADMIN_TOKEN not set', () => {
      delete process.env.ADMIN_TOKEN
      
      const request = new Request('http://test.com', {
        headers: {
          'authorization': 'Bearer any-token'
        }
      })
      
      expect(() => requireAdmin(request)).toThrow('ADMIN_TOKEN environment variable not set')
    })
  })
})
