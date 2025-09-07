import { safeName, shardPath } from '../lib/disk'

describe('Disk Utilities', () => {
  describe('safeName', () => {
    it('should preserve safe characters', () => {
      expect(safeName('resume_v1.pdf')).toBe('resume_v1.pdf')
      expect(safeName('document-2024.docx')).toBe('document-2024.docx')
      expect(safeName('file123.pdf')).toBe('file123.pdf')
    })

    it('should replace unsafe characters with underscores', () => {
      expect(safeName('résumé with spaces.pdf')).toBe('r_sum__with_spaces.pdf')
      expect(safeName('file@#$.pdf')).toBe('file___.pdf')
      expect(safeName('path/to/file.pdf')).toBe('path_to_file.pdf')
    })

    it('should handle empty strings', () => {
      expect(safeName('')).toBe('')
    })

    it('should handle strings with only unsafe characters', () => {
      expect(safeName('@#$%^&*()')).toBe('_________')
    })
  })

  describe('shardPath', () => {
    it('should generate consistent paths for same input', () => {
      const id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
      const filename = 'test.pdf'
      
      const result1 = shardPath(id, filename)
      const result2 = shardPath(id, filename)
      
      expect(result1.rel).toBe(result2.rel)
      expect(result1.abs).toBe(result2.abs)
    })

    it('should create proper directory structure', () => {
      const id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
      const filename = 'resume.pdf'
      
      const result = shardPath(id, filename)
      
      // Should have format: uploads/xx/yy/uuid__filename
      expect(result.rel).toMatch(/^uploads\/[a-f0-9]{2}\/[a-f0-9]{2}\/[a-f0-9-]+__resume\.pdf$/)
      expect(result.abs).toContain(result.rel)
    })

    it('should handle special characters in filename', () => {
      const id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
      const filename = 'résumé with spaces!.pdf'
      
      const result = shardPath(id, filename)
      
      // Filename should be sanitized
      expect(result.rel).toContain('r_sum__with_spaces_.pdf')
    })

    it('should generate different paths for different IDs', () => {
      const id1 = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
      const id2 = 'b2c3d4e5-f6a7-8901-bcde-f23456789012'
      const filename = 'test.pdf'
      
      const result1 = shardPath(id1, filename)
      const result2 = shardPath(id2, filename)
      
      expect(result1.rel).not.toBe(result2.rel)
    })
  })
})
