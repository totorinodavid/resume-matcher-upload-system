# Test Database Setup Guide

## Quick Local PostgreSQL Setup

### Option 1: Docker (Recommended)
```bash
# Start test database
docker run --name resume-matcher-test-db \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_DB=resume_matcher_test \
  -p 5433:5432 \
  -d postgres:15

# Set environment variables
export ASYNC_DATABASE_URL="postgresql+asyncpg://testuser:testpass@localhost:5433/resume_matcher_test"
export SYNC_DATABASE_URL="postgresql+psycopg://testuser:testpass@localhost:5433/resume_matcher_test"

# Run tests
pytest tests/credits/ -v
```

### Option 2: Use Your Existing Neon Database
```bash
# Use your existing Neon database (be careful - this will create test data)
export ASYNC_DATABASE_URL="your_neon_async_url_here"
export SYNC_DATABASE_URL="your_neon_sync_url_here"

# Run tests
pytest tests/credits/ -v
```

### Option 3: PostgreSQL with Windows
```powershell
# If you have PostgreSQL installed locally
$env:ASYNC_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/resume_matcher_test"
$env:SYNC_DATABASE_URL="postgresql+psycopg://postgres:password@localhost:5432/resume_matcher_test"

# Run tests
pytest tests/credits/ -v
```

## Test Commands

### Run All Credits Tests
```bash
pytest tests/credits/ -v
```

### Run Specific Test Categories
```bash
# Happy path tests (6 tests)
pytest tests/credits/test_happy_path.py -v

# Idempotency tests (6 tests)  
pytest tests/credits/test_idempotency.py -v

# Negative/error tests (10 tests)
pytest tests/credits/test_negative_cases.py -v
```

### Run with Coverage
```bash
pytest tests/credits/ --cov=app --cov-report=html
```

### Run Single Test
```bash
pytest tests/credits/test_happy_path.py::TestHappyPath::test_purchase_credits -v
```

## Database Schema Verification

The tests will automatically:
1. Create all required tables (users, payments, credit_transactions, etc.)
2. Set up proper foreign key relationships
3. Initialize test data
4. Clean up after each test

## Test Results Expected

✅ **22 total tests** should pass:
- 6 happy path tests (successful credit purchases)
- 6 idempotency tests (duplicate webhook handling)
- 10 negative tests (error cases and validation)

If tests fail, check:
1. Database connection URLs are correct
2. Database user has CREATE TABLE permissions
3. All required packages are installed (`pytest`, `pytest-asyncio`, `pytest-cov`)
