# Credits System Test Suite

This directory contains comprehensive pytest tests for the production credits system using SQLAlchemy Async with PostgreSQL.

## Test Structure

```
tests/
├── conftest.py                     # Test fixtures and helper functions
├── credits/
│   ├── __init__.py
│   ├── test_happy_path.py          # Successful credit purchase flows
│   ├── test_idempotency.py         # Duplicate operation prevention
│   └── test_negative_cases.py      # Error conditions and constraints
└── README.md                       # This file
```

## Test Coverage

### Happy Path Tests (`test_happy_path.py`)
- ✅ Successful credit purchase with balance updates
- ✅ Multiple purchases accumulating correctly
- ✅ Foreign key relationships across all tables
- ✅ INSERT/UPDATE RETURNING validation
- ✅ Currency and amount consistency
- ✅ Row count verification

### Idempotency Tests (`test_idempotency.py`)
- ✅ Duplicate payment intent rejection (unique constraints)
- ✅ Same intent ID allowed for different providers
- ✅ Credit application idempotency detection
- ✅ Processed events webhook deduplication
- ✅ Concurrent credit application safety
- ✅ Transaction rollback isolation

### Negative Cases (`test_negative_cases.py`)
- ✅ Unpaid payments don't generate credits
- ✅ Invalid foreign key constraints
- ✅ Invalid data types and formats
- ✅ Negative credit transactions (refunds)
- ✅ Insufficient balance scenarios
- ✅ Missing required fields
- ✅ Invalid currency formats
- ✅ Zero amount payments
- ✅ Large value handling

## Requirements

The tests require the following packages to be installed:

```bash
pip install pytest pytest-asyncio asyncpg psycopg psycopg-binary
```

## Environment Setup

Set the following environment variables for your test database:

```bash
# Required: PostgreSQL test database URLs
export ASYNC_DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/test_db"
export SYNC_DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/test_db"

# Optional: Disable background tasks during testing
export DISABLE_BACKGROUND_TASKS="true"
```

### Using Neon PostgreSQL (Recommended)

For Neon PostgreSQL (production-like environment):

```bash
export ASYNC_DATABASE_URL="postgresql+asyncpg://user:password@ep-xxxxx.us-west-2.aws.neon.tech/test_db?sslmode=require"
export SYNC_DATABASE_URL="postgresql+psycopg://user:password@ep-xxxxx.us-west-2.aws.neon.tech/test_db?sslmode=require"
```

## Running Tests

### Run All Credits Tests
```bash
cd apps/backend
pytest tests/credits/ -v
```

### Run Specific Test Categories
```bash
# Happy path tests only
pytest tests/credits/test_happy_path.py -v

# Idempotency tests only
pytest tests/credits/test_idempotency.py -v

# Negative cases only
pytest tests/credits/test_negative_cases.py -v
```

### Run with Coverage
```bash
pytest tests/credits/ --cov=app.services --cov=app.models --cov-report=html
```

### Run Tests in Parallel (faster)
```bash
pytest tests/credits/ -n auto
```

### Verbose Output with Timing
```bash
pytest tests/credits/ -v --durations=10
```

## Test Design Principles

### 🔄 **Transaction Isolation**
Each test runs in its own database transaction that gets rolled back at the end. This ensures:
- No persistent changes to the database
- Tests can run in any order
- No test data pollution between tests

### 🎯 **Deterministic Data**
- All test data uses `uuid4()` for unique identifiers
- No hardcoded IDs like `1`, `2`, `3`
- Each test creates its own isolated test data

### ✅ **Strict Assertions**
- No `print()` statements for success indication
- Every assertion validates specific expected behavior
- Row counts, balance amounts, and foreign key relationships are explicitly verified

### 🚀 **Real Database Operations**
- No mocking of SQL operations
- Tests run against actual PostgreSQL/Neon database
- Full integration testing of database constraints and triggers

### 🛡️ **Error Condition Testing**
- Tests verify constraint violations raise appropriate exceptions
- Foreign key constraints are validated
- Data type errors are caught and verified

## Test Fixtures

### Core Fixtures (from `conftest.py`)

- **`db_conn`**: Isolated database connection with transaction rollback
- **`db_session`**: SQLAlchemy async session (existing, enhanced)

### Helper Functions

- **`insert_user()`**: Create test user with unique email/ID
- **`insert_payment()`**: Create test payment with proper relationships
- **`apply_credit_purchase()`**: Execute credit purchase business logic
- **`get_user_balance()`**: Retrieve current user credit balance
- **`count_credit_transactions()`**: Count transactions with optional filters
- **`payment_exists_by_intent()`**: Check payment existence by provider/intent ID

## Database Schema Requirements

The tests expect the following PostgreSQL tables to exist:

```sql
-- Users table with credits_balance column
CREATE TABLE users (
    id TEXT PRIMARY KEY,  -- UUID as text
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    credits_balance INTEGER NOT NULL DEFAULT 0
);

-- Payments table with constraints
CREATE TABLE payments (
    id TEXT PRIMARY KEY,  -- UUID as text  
    user_id TEXT NOT NULL REFERENCES users(id),
    provider TEXT NOT NULL,
    provider_payment_intent_id TEXT,
    amount_total_cents INTEGER NOT NULL CHECK (amount_total_cents >= 0),
    currency TEXT NOT NULL,
    expected_credits INTEGER NOT NULL CHECK (expected_credits >= 0),
    status TEXT NOT NULL,
    raw_provider_data JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(provider, provider_payment_intent_id)
);

-- Credit transactions (audit log)
CREATE TABLE credit_transactions (
    id TEXT PRIMARY KEY,  -- UUID as text
    user_id TEXT NOT NULL REFERENCES users(id),
    payment_id TEXT REFERENCES payments(id),
    admin_action_id TEXT,
    delta_credits INTEGER NOT NULL,
    reason TEXT NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Processed events (webhook idempotency)
CREATE TABLE processed_events (
    id TEXT PRIMARY KEY,  -- UUID as text
    provider TEXT NOT NULL,
    provider_event_id TEXT NOT NULL,
    received_at TIMESTAMPTZ DEFAULT now(),
    payload_sha256 TEXT NOT NULL,
    UNIQUE(provider, provider_event_id)
);
```

## Continuous Integration

For CI/CD pipelines, use the following pytest configuration:

```bash
# In CI environment
pytest tests/credits/ \
  --verbose \
  --tb=short \
  --strict-markers \
  --disable-warnings \
  --maxfail=5
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `apps/backend` is in your Python path
2. **Database Connection**: Verify `DATABASE_URL` environment variables
3. **Permission Errors**: Ensure test database user has CREATE/DROP privileges
4. **Migration State**: Run `alembic upgrade head` before tests if needed

### Debug Mode

Run tests with extra debugging:

```bash
pytest tests/credits/ -v -s --log-cli-level=DEBUG
```

### Test Database Reset

If tests are failing due to database state issues:

```bash
# Reset test database (be careful!)
psql $SYNC_DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
alembic upgrade head
```

## Performance

Expected test runtime:
- **Happy Path**: ~5-10 seconds (6 tests)
- **Idempotency**: ~8-15 seconds (6 tests) 
- **Negative Cases**: ~10-20 seconds (10 tests)
- **Total**: ~25-45 seconds for full suite

Tests are designed to be fast and can run in parallel with `pytest-xdist`.
