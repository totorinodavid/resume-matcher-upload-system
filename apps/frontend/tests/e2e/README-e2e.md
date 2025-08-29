E2E Test Notes

- Service Worker is disabled during tests to avoid offline fallback.
- Strict tests use @clerk/testing to sign in programmatically. Ensure env:
  - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  - CLERK_SECRET_KEY
  - E2E_CLERK_EMAIL
  - E2E_CLERK_PASSWORD
