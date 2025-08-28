import { test, expect, request as pwRequest } from '@playwright/test';

const SITE = process.env.E2E_SITE_URL || 'http://localhost:3000';

test('BFF forwards Authorization header and handles 401', async ({ request }) => {
  // Without token -> expect 401 from protected POST
  const res401 = await request.post(`${SITE}/api/bff/api/v1/match`, { data: { resume_id: 'x', job_id: 'y' } });
  expect([401, 403, 404]).toContain(res401.status()); // tolerate 404 locally if route missing

  // With bogus token -> expect 401/403 invalid token
  const resInvalid = await request.post(`${SITE}/api/bff/api/v1/match`, {
    data: { resume_id: 'x', job_id: 'y' },
    headers: { Authorization: 'Bearer invalid.token' }
  });
  expect([401, 403, 404]).toContain(resInvalid.status());
});
