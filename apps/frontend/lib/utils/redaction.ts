// PII Redaction utilities for Resume Matcher logging
// Ensures sensitive user data is not logged in production

export interface RedactionOptions {
  showFirst?: number
  showLast?: number
  maskChar?: string
  preserveDomain?: boolean // For emails
}

export const redactionUtils = {
  // Redact email addresses
  email(email: string, options: RedactionOptions = {}): string {
    if (!email || typeof email !== 'string') return '[INVALID_EMAIL]'
    
    const { preserveDomain = true, maskChar = '*' } = options
    
    if (preserveDomain) {
      const [localPart, domain] = email.split('@')
      if (!domain) return '[INVALID_EMAIL]'
      
      const redactedLocal = localPart.length > 2 
        ? localPart[0] + maskChar.repeat(localPart.length - 2) + localPart[localPart.length - 1]
        : maskChar.repeat(localPart.length)
      
      return `${redactedLocal}@${domain}`
    }
    
    return this.generic(email, { showFirst: 2, showLast: 0, maskChar })
  },

  // Redact generic strings (names, IDs, etc.)
  generic(value: string, options: RedactionOptions = {}): string {
    if (!value || typeof value !== 'string') return '[REDACTED]'
    
    const { showFirst = 1, showLast = 1, maskChar = '*' } = options
    const totalShow = showFirst + showLast
    
    if (value.length <= totalShow) {
      return maskChar.repeat(value.length)
    }
    
    const start = value.substring(0, showFirst)
    const end = showLast > 0 ? value.substring(value.length - showLast) : ''
    const middle = maskChar.repeat(value.length - totalShow)
    
    return start + middle + end
  },

  // Redact user ID (show only first few characters)
  userId(id: string | number): string {
    const idStr = id.toString()
    return this.generic(idStr, { showFirst: 2, showLast: 0, maskChar: 'X' })
  },

  // Redact Stripe customer ID
  stripeCustomerId(customerId: string): string {
    if (!customerId || !customerId.startsWith('cus_')) {
      return '[INVALID_CUSTOMER_ID]'
    }
    return 'cus_' + this.generic(customerId.substring(4), { showFirst: 2, showLast: 2 })
  },

  // Redact credit card information
  creditCard(cardNumber: string): string {
    if (!cardNumber) return '[NO_CARD]'
    const cleaned = cardNumber.replace(/\D/g, '')
    if (cleaned.length < 4) return '[INVALID_CARD]'
    
    return '****-****-****-' + cleaned.slice(-4)
  },

  // Redact phone numbers
  phone(phoneNumber: string): string {
    if (!phoneNumber) return '[NO_PHONE]'
    const cleaned = phoneNumber.replace(/\D/g, '')
    if (cleaned.length < 4) return '[INVALID_PHONE]'
    
    return '***-***-' + cleaned.slice(-4)
  },

  // Redact IP addresses
  ipAddress(ip: string): string {
    if (!ip) return '[NO_IP]'
    
    if (ip.includes(':')) {
      // IPv6
      const parts = ip.split(':')
      return parts.slice(0, 2).join(':') + ':****:****:****:' + parts.slice(-1)[0]
    } else {
      // IPv4
      const parts = ip.split('.')
      if (parts.length !== 4) return '[INVALID_IP]'
      return parts[0] + '.***.***.***'
    }
  },

  // Redact object with multiple PII fields
  object<T extends Record<string, any>>(
    obj: T,
    fieldsToRedact: Array<keyof T>,
    customRedactors?: Partial<Record<keyof T, (value: any) => string>>
  ): T {
    if (!obj || typeof obj !== 'object') return obj
    
    const redacted = { ...obj }
    
    fieldsToRedact.forEach(field => {
      if (field in redacted) {
        const customRedactor = customRedactors?.[field]
        if (customRedactor) {
          (redacted as any)[field] = customRedactor(redacted[field])
        } else {
          // Auto-detect redaction type based on field name
          const fieldName = String(field).toLowerCase()
          
          if (fieldName.includes('email')) {
            (redacted as any)[field] = this.email(redacted[field])
          } else if (fieldName.includes('phone')) {
            (redacted as any)[field] = this.phone(redacted[field])
          } else if (fieldName.includes('ip')) {
            (redacted as any)[field] = this.ipAddress(redacted[field])
          } else if (fieldName.includes('card') || fieldName.includes('credit')) {
            (redacted as any)[field] = this.creditCard(redacted[field])
          } else {
            (redacted as any)[field] = this.generic(redacted[field])
          }
        }
      }
    })
    
    return redacted
  }
}

// Convenience function for most common use case
export function redact(value: string, type: 'email' | 'generic' | 'userId' | 'stripe' = 'generic'): string {
  switch (type) {
    case 'email':
      return redactionUtils.email(value)
    case 'userId':
      return redactionUtils.userId(value)
    case 'stripe':
      return redactionUtils.stripeCustomerId(value)
    default:
      return redactionUtils.generic(value)
  }
}

// Resume Matcher specific redaction patterns
export const resumeMatcherRedaction = {
  // Redact user for logging - handles null values
  user(user: { id?: number; email?: string | null; name?: string | null }) {
    return redactionUtils.object({
      id: user.id,
      email: user.email ?? undefined,
      name: user.name ?? undefined
    }, ['email', 'name'], {
      id: (id) => redactionUtils.userId(id),
      email: (email) => redactionUtils.email(email),
      name: (name) => redactionUtils.generic(name, { showFirst: 1, showLast: 0 })
    })
  },

  // Redact credit transaction for logging
  creditTransaction(transaction: {
    id?: string;
    userId?: number;
    delta_credits?: number;
    stripeEventId?: string;
    meta?: any;
  }) {
    return {
      id: transaction.id ? redactionUtils.generic(transaction.id, { showFirst: 3, showLast: 3 }) : undefined,
      userId: transaction.userId ? redactionUtils.userId(transaction.userId) : undefined,
      delta_credits: transaction.delta_credits, // Credits amount is not PII
      stripeEventId: transaction.stripeEventId ? 'evt_' + redactionUtils.generic(transaction.stripeEventId.replace('evt_', ''), { showFirst: 3, showLast: 3 }) : undefined,
      meta: transaction.meta ? '[METADATA_REDACTED]' : undefined
    }
  },

  // Redact Stripe event for logging
  stripeEvent(event: {
    id?: string;
    type?: string;
    data?: any;
    created?: number;
  }) {
    return {
      id: event.id ? 'evt_' + redactionUtils.generic(event.id.replace('evt_', ''), { showFirst: 3, showLast: 3 }) : undefined,
      type: event.type, // Event type is not PII
      created: event.created, // Timestamp is not PII
      data: '[DATA_REDACTED]' // Stripe data may contain PII
    }
  }
}

export default redactionUtils