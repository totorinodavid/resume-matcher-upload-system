# ------------------------------------------------------------------
# 6) SQL: Schnelle Verifikation
# ------------------------------------------------------------------
# Quick verification queries for the hotfix implementation

-- A) Check if credits_balance column exists
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns
WHERE table_name='users' AND column_name='credits_balance';

-- B) Check if stripe_events table exists
SELECT 
    table_name, 
    table_type
FROM information_schema.tables
WHERE table_name='stripe_events';

-- C) Check constraints on users table
SELECT 
    constraint_name, 
    constraint_type, 
    check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_name = 'users';

-- D) Check indexes on users table
SELECT 
    indexname, 
    indexdef
FROM pg_indexes
WHERE tablename = 'users';

-- E) Sample users data (safe query)
SELECT 
    id, 
    email, 
    name, 
    credits_balance
FROM users 
LIMIT 5;

-- F) Check if any stripe events have been processed
SELECT 
    COUNT(*) as total_events,
    COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed_events,
    COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed_events
FROM stripe_events;

-- G) Recent stripe events (if any)
SELECT 
    event_id,
    event_type,
    processing_status,
    processed_at,
    error_message
FROM stripe_events
ORDER BY processed_at DESC
LIMIT 10;

-- H) Users with credits
SELECT 
    id,
    email,
    name,
    credits_balance
FROM users
WHERE credits_balance > 0
ORDER BY credits_balance DESC
LIMIT 10;

-- I) UUID test query (adapt UUID as needed)
-- SELECT id, email, name FROM users WHERE id = '00000000-0000-0000-0000-000000000000'::UUID;

-- J) Email query test
-- SELECT id, email, name FROM users WHERE email = 'test@example.com';

-- K) Test credits_balance constraint (should fail if constraint works)
-- INSERT INTO users (email, name, credits_balance) VALUES ('test@constraint.com', 'Test User', -1);

-- L) Test email uniqueness (should fail on second insert)
-- INSERT INTO users (email, name) VALUES ('unique@test.com', 'User 1');
-- INSERT INTO users (email, name) VALUES ('unique@test.com', 'User 2');
