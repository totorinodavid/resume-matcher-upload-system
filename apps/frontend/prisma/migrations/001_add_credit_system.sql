-- Resume Matcher Credit System Migration
-- Creates tables for Stripe credit system with ledger approach

-- Create enum for credit transaction reasons
CREATE TYPE "CreditReason" AS ENUM (
  'purchase',
  'refund', 
  'resume_analysis',
  'job_match',
  'resume_improvement',
  'manual',
  'bonus',
  'welcome'
);

-- Add Stripe and credit columns to existing users table
ALTER TABLE "users" 
ADD COLUMN IF NOT EXISTS "stripe_customer_id" TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS "credits_balance" INTEGER NOT NULL DEFAULT 0;

-- Create credit transactions ledger table
CREATE TABLE IF NOT EXISTS "credit_transactions" (
    "id" BIGSERIAL PRIMARY KEY,
    "user_id" INTEGER NOT NULL,
    "delta_credits" INTEGER NOT NULL,
    "reason" "CreditReason" NOT NULL,
    "stripe_event_id" TEXT UNIQUE,
    "meta" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT "credit_transactions_user_id_fkey" 
        FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE
);

-- Create price mapping table for local cache
CREATE TABLE IF NOT EXISTS "prices" (
    "stripe_price_id" TEXT PRIMARY KEY,
    "credits_per_unit" INTEGER NOT NULL,
    "price_in_cents" INTEGER NOT NULL,
    "currency" TEXT NOT NULL DEFAULT 'eur',
    "active" BOOLEAN NOT NULL DEFAULT true,
    "name" TEXT,
    "description" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS "credit_transactions_user_id_created_at_idx" 
    ON "credit_transactions"("user_id", "created_at" DESC);

CREATE INDEX IF NOT EXISTS "credit_transactions_reason_idx" 
    ON "credit_transactions"("reason");

CREATE INDEX IF NOT EXISTS "credit_transactions_stripe_event_id_idx" 
    ON "credit_transactions"("stripe_event_id") 
    WHERE "stripe_event_id" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "users_stripe_customer_id_idx" 
    ON "users"("stripe_customer_id") 
    WHERE "stripe_customer_id" IS NOT NULL;

-- Insert default credit packages
INSERT INTO "prices" (
    "stripe_price_id", 
    "credits_per_unit", 
    "price_in_cents", 
    "currency",
    "name",
    "description",
    "active"
) VALUES 
    ('price_starter_placeholder', 100, 500, 'eur', 'Starter Pack', '10 resume analyses or 20 job matches', true),
    ('price_pro_placeholder', 500, 2000, 'eur', 'Pro Pack', '50 resume analyses + improvements', true),
    ('price_premium_placeholder', 1200, 3500, 'eur', 'Premium Pack', 'Everything included with 20% bonus', true)
ON CONFLICT ("stripe_price_id") DO NOTHING;

-- Create function to recalculate user credit balance from transactions
CREATE OR REPLACE FUNCTION recalculate_user_credits(target_user_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    total_credits INTEGER;
BEGIN
    SELECT COALESCE(SUM(delta_credits), 0) 
    INTO total_credits
    FROM credit_transactions 
    WHERE user_id = target_user_id;
    
    UPDATE users 
    SET credits_balance = total_credits 
    WHERE id = target_user_id;
    
    RETURN total_credits;
END;
$$ LANGUAGE plpgsql;

-- Create function to verify credit balance consistency
CREATE OR REPLACE FUNCTION verify_credit_balances()
RETURNS TABLE(user_id INTEGER, calculated_balance INTEGER, stored_balance INTEGER, difference INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id as user_id,
        COALESCE(SUM(ct.delta_credits), 0)::INTEGER as calculated_balance,
        u.credits_balance as stored_balance,
        (u.credits_balance - COALESCE(SUM(ct.delta_credits), 0))::INTEGER as difference
    FROM users u
    LEFT JOIN credit_transactions ct ON u.id = ct.user_id
    GROUP BY u.id, u.credits_balance
    HAVING u.credits_balance != COALESCE(SUM(ct.delta_credits), 0);
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update user balance on transaction insert
CREATE OR REPLACE FUNCTION update_user_balance_trigger()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET credits_balance = credits_balance + NEW.delta_credits
    WHERE id = NEW.user_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Only create trigger if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger 
        WHERE tgname = 'credit_transaction_balance_update'
    ) THEN
        CREATE TRIGGER credit_transaction_balance_update
            AFTER INSERT ON credit_transactions
            FOR EACH ROW
            EXECUTE FUNCTION update_user_balance_trigger();
    END IF;
END $$;

-- Add helpful comments
COMMENT ON TABLE "credit_transactions" IS 'Ledger table tracking all credit additions and deductions';
COMMENT ON COLUMN "credit_transactions"."delta_credits" IS 'Positive for credits added, negative for credits spent';
COMMENT ON COLUMN "credit_transactions"."stripe_event_id" IS 'Stripe event ID for idempotency - prevents duplicate processing';
COMMENT ON COLUMN "credit_transactions"."meta" IS 'Additional metadata like resumeId, jobId, sessionId etc';

COMMENT ON TABLE "prices" IS 'Local cache of Stripe price data for credit packages';
COMMENT ON COLUMN "users"."credits_balance" IS 'Current credit balance - calculated from transaction ledger';
COMMENT ON COLUMN "users"."stripe_customer_id" IS 'Stripe customer ID for payment processing';

-- Create view for credit usage analytics
CREATE OR REPLACE VIEW credit_usage_analytics AS
SELECT 
    reason,
    COUNT(*) as transaction_count,
    SUM(ABS(delta_credits)) as total_credits_used,
    AVG(ABS(delta_credits)) as avg_credits_per_transaction,
    MIN(created_at) as first_usage,
    MAX(created_at) as last_usage
FROM credit_transactions 
WHERE delta_credits < 0  -- Only spending transactions
GROUP BY reason
ORDER BY total_credits_used DESC;

COMMENT ON VIEW credit_usage_analytics IS 'Analytics view for credit spending patterns by feature';

-- Create view for user credit summaries
CREATE OR REPLACE VIEW user_credit_summaries AS
SELECT 
    u.id as user_id,
    u.email,
    u.credits_balance,
    COALESCE(purchase_stats.total_purchased, 0) as total_purchased,
    COALESCE(spend_stats.total_spent, 0) as total_spent,
    COALESCE(transaction_stats.transaction_count, 0) as transaction_count,
    COALESCE(transaction_stats.last_transaction, NULL) as last_transaction
FROM users u
LEFT JOIN (
    SELECT 
        user_id,
        SUM(delta_credits) as total_purchased
    FROM credit_transactions 
    WHERE delta_credits > 0 
    GROUP BY user_id
) purchase_stats ON u.id = purchase_stats.user_id
LEFT JOIN (
    SELECT 
        user_id,
        SUM(ABS(delta_credits)) as total_spent
    FROM credit_transactions 
    WHERE delta_credits < 0 
    GROUP BY user_id
) spend_stats ON u.id = spend_stats.user_id
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as transaction_count,
        MAX(created_at) as last_transaction
    FROM credit_transactions 
    GROUP BY user_id
) transaction_stats ON u.id = transaction_stats.user_id;

COMMENT ON VIEW user_credit_summaries IS 'Summary view of user credit activity for dashboard/admin';

-- Grant appropriate permissions (adjust based on your user setup)
-- GRANT SELECT, INSERT, UPDATE ON credit_transactions TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON prices TO app_user;
-- GRANT EXECUTE ON FUNCTION recalculate_user_credits(INTEGER) TO app_user;
-- GRANT EXECUTE ON FUNCTION verify_credit_balances() TO app_user;
