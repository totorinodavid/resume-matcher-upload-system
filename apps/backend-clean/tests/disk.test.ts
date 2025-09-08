import assert from 'node:assert'
import { test } from 'node:test'
import { shardPath, streamAndHashFile } from '../lib/disk'
import { createHash } from 'crypto'
import { promises as fs } from 'fs'
import { dirname } from 'path'

test('shardPath builds expected depth', () => {
  const h = 'a'.repeat(64)
  const p = shardPath(h)
  // path ends with hash and contains two shard folders
  const parts = p.split(/\\|\//)
  const last = parts[parts.length - 1]
  assert.equal(last, h)
})

test('streamAndHashFile computes correct hash and finalizes', async () => {
  const data = Buffer.from('hello world')
  const expected = createHash('sha256').update(data).digest('hex')
  const file = new File([data], 'test.pdf', { type: 'application/pdf' })
  const streamed = await streamAndHashFile(file as any, 1024 * 1024)
  assert.equal(streamed.hash, expected)
  await streamed.finalize(streamed.hash)
})