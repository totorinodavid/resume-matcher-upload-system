// Wait for Postgres to become reachable, then run pending migrations (idempotent)
// Retries keep build/start separation clean so build doesn’t fail when DB is briefly unavailable.
const { PrismaClient } = require('@prisma/client')

const prisma = new PrismaClient()
const MAX_RETRIES = parseInt(process.env.DB_WAIT_MAX_RETRIES || '30', 10)
const DELAY_MS = parseInt(process.env.DB_WAIT_DELAY_MS || '2000', 10)

async function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

async function ping() {
  // Lightweight query; SELECT 1 sometimes blocked on some hosts => use a trivial aggregate
  await prisma.$queryRaw`SELECT 1 as ok`
}

async function main() {
  if (process.env.SKIP_DB_WAIT === '1') {
    console.log('[db-wait] SKIP_DB_WAIT=1 -> skipping wait & migrate')
    return
  }
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      await ping()
      console.log(`[db-wait] database reachable on attempt ${attempt}`)
      break
    } catch (e) {
      const code = e.code || e.errno || e.message
      console.log(`[db-wait] attempt ${attempt}/${MAX_RETRIES} failed: ${code}`)
      if (attempt === MAX_RETRIES) {
        console.error('[db-wait] giving up; continuing WITHOUT running migrations')
        return
      }
      await sleep(DELAY_MS)
    }
  }
  try {
    console.log('[db-wait] running prisma migrate deploy (idempotent)')
    // Use child process to avoid bundling prisma engine into this file manually
    const { spawn } = require('child_process')
    await new Promise((res, rej) => {
      const p = spawn('npx', ['prisma', 'migrate', 'deploy'], { stdio: 'inherit' })
      p.on('exit', (code) => code === 0 ? res() : rej(new Error('migrate exit '+code)))
    })
    console.log('[db-wait] migrations applied (or already up-to-date)')
  } catch (e) {
    console.error('[db-wait] migration step failed:', e.message)
  } finally {
    await prisma.$disconnect().catch(()=>{})
  }
}

main().catch(e => { console.error('[db-wait] fatal', e); process.exit(0) })
