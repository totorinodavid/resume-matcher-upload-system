E2E Test Notes

- Service Worker is disabled during tests to avoid offline fallback.
- Strict tests use NextAuth.js testing to sign in programmatically. Ensure env:
  - NEXTAUTH_SECRET
  - NEXTAUTH_URL
  - E2E_TEST_EMAIL
  - E2E_TEST_PASSWORD
