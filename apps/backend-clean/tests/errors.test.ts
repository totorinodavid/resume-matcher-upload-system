import { err } from '../lib/errors'
import assert from 'node:assert'
import { test } from 'node:test'

test('err helper returns expected shape', () => {
  const e = err('code_x', 'Message', { a: 1 })
  assert.equal(e.error, 'code_x')
  assert.equal(e.message, 'Message')
  assert.deepEqual(e.details, { a: 1 })
})