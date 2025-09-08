import { logger } from './logger'

interface AppConfig {
  databaseUrl: string
  filesDir: string
  rateLimitTokens: number
  rateLimitWindowMs: number
  diskTotalBytes: number
  adminToken?: string
  adminTokenHash?: string
}

function requireEnv(name: string): string {
  const v = process.env[name]
  if (!v || !v.trim()) {
    throw new Error(`Missing required env: ${name}`)
  }
  return v
}

function intEnv(name: string, def: number, min = 1): number {
  const raw = process.env[name]
  if (!raw) return def
  const n = parseInt(raw, 10)
  if (Number.isNaN(n) || n < min) {
    throw new Error(`Invalid numeric env ${name}='${raw}' (min ${min})`)
  }
  return n
}

function buildConfig(): AppConfig {
  const databaseUrl = requireEnv('DATABASE_URL')
  const filesDir = process.env.FILES_DIR || '/var/data'
  const rateLimitTokens = intEnv('RATE_LIMIT_TOKENS', 30, 1)
  const rateLimitWindowMs = intEnv('RATE_LIMIT_WINDOW_MS', 60_000, 100)
  const diskTotalBytes = intEnv('DISK_TOTAL_BYTES', 10 * 1024 * 1024 * 1024, 1024)
  const adminToken = process.env.ADMIN_TOKEN
  const adminTokenHash = process.env.ADMIN_TOKEN_HASH

  if (!adminToken && !adminTokenHash) {
    logger.warn('config.admin_token_missing', { msg: 'No ADMIN_TOKEN / ADMIN_TOKEN_HASH set; admin endpoints unusable' })
  }

  return {
    databaseUrl,
    filesDir,
    rateLimitTokens,
    rateLimitWindowMs,
    diskTotalBytes,
    adminToken,
    adminTokenHash
  }
}

export const config = buildConfig()
