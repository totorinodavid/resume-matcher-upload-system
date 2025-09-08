type LogLevel = 'info' | 'warn' | 'error'

interface LogBase {
  level: LogLevel
  time: string
  msg: string
  reqId?: string
  [key: string]: any
}

const useStdout = typeof process !== 'undefined' && !!(process as any).stdout && typeof (process as any).stdout.write === 'function'

function write(entry: LogBase) {
  // Single line JSON for easy ingestion; fall back to console on Edge runtime (no process.stdout)
  const line = JSON.stringify(entry)
  if (useStdout) {
    ;(process as any).stdout.write(line + '\n')
  } else {
    console.log(line)
  }
}

export function log(level: LogLevel, msg: string, data?: Record<string, any>) {
  write({ level, time: new Date().toISOString(), msg, ...data })
}

export const logger = {
  info: (msg: string, data?: Record<string, any>) => log('info', msg, data),
  warn: (msg: string, data?: Record<string, any>) => log('warn', msg, data),
  error: (msg: string, data?: Record<string, any>) => log('error', msg, data)
}

export function withReqId(headers: Headers): string {
  const existing = headers.get('x-request-id')
  if (existing) return existing
  // lightweight random id
  return Math.random().toString(36).slice(2, 10)
}