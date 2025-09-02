-- EMERGENCY DATABASE FIX - Direct SQL
-- Run this on production database to fix missing columns

-- 1. Add credits_balance column to users table if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'credits_balance'
    ) THEN
        ALTER TABLE users ADD COLUMN credits_balance INTEGER DEFAULT 0 NOT NULL;
    END IF;
END $$;

-- 2. Check and fix payments table structure
DO $$
BEGIN
    -- Add stripe_session_id if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'payments' AND column_name = 'stripe_session_id'
    ) THEN
        ALTER TABLE payments ADD COLUMN stripe_session_id VARCHAR(255);
    END IF;
    
    -- Add stripe_payment_intent_id if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'payments' AND column_name = 'stripe_payment_intent_id'
    ) THEN
        ALTER TABLE payments ADD COLUMN stripe_payment_intent_id VARCHAR(255);
    END IF;
    
    -- Add currency if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'payments' AND column_name = 'currency'
    ) THEN
        ALTER TABLE payments ADD COLUMN currency VARCHAR(3) DEFAULT 'usd';
    END IF;
    
    -- Add credits_granted if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'payments' AND column_name = 'credits_granted'
    ) THEN
        ALTER TABLE payments ADD COLUMN credits_granted INTEGER DEFAULT 0;
    END IF;
    
    -- Add metadata if missing
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'payments' AND column_name = 'metadata'
    ) THEN
        ALTER TABLE payments ADD COLUMN metadata JSONB;
    END IF;
END $$;

-- 3. Create missing tables if they don't exist

-- Create payment status enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentstatus') THEN
        CREATE TYPE paymentstatus AS ENUM ('pending', 'completed', 'failed', 'cancelled', 'refunded');
    END IF;
END $$;

-- Create stripe_customers table
CREATE TABLE IF NOT EXISTS stripe_customers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_customer_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create credit_transactions table
CREATE TABLE IF NOT EXISTS credit_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL,
    amount INTEGER NOT NULL,
    balance_before INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create processed_events table
CREATE TABLE IF NOT EXISTS processed_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- 4. Create indexes
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_processed_events_event_id ON processed_events(event_id);

-- Only create stripe_session_id index if column exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'payments' AND column_name = 'stripe_session_id'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_payments_stripe_session ON payments(stripe_session_id);
    END IF;
END $$;

-- Add unique constraint on stripe_session_id if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'payments' 
        AND constraint_name = 'payments_stripe_session_id_unique'
    ) THEN
        -- Only if column exists and constraint doesn't exist
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'payments' AND column_name = 'stripe_session_id'
        ) THEN
            ALTER TABLE payments ADD CONSTRAINT payments_stripe_session_id_unique UNIQUE (stripe_session_id);
        END IF;
    END IF;
END $$;

-- 5. Verify the fix - show table structures
SELECT 'USERS TABLE STRUCTURE:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users'
ORDER BY ordinal_position;

SELECT 'PAYMENTS TABLE STRUCTURE:' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'payments'
ORDER BY ordinal_position;
