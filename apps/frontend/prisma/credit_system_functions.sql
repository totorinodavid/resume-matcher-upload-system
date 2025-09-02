-- Additional functions and views for the credit system
-- This file contains the functions that need to be added after the schema is created

-- Function to recalculate credit balance for a user
CREATE OR REPLACE FUNCTION recalculate_user_credits(user_id_param INTEGER)
RETURNS INTEGER AS $$
DECLARE
    calculated_balance INTEGER;
BEGIN
    SELECT COALESCE(SUM(delta_credits), 0)
    INTO calculated_balance
    FROM credit_transactions
    WHERE user_id = user_id_param;
    
    UPDATE users
    SET credits_balance = calculated_balance,
        updated_at = NOW()
    WHERE id = user_id_param;
    
    RETURN calculated_balance;
END;
$$ LANGUAGE plpgsql;

-- Function to verify credit balance consistency
CREATE OR REPLACE FUNCTION verify_credit_balance(user_id_param INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    stored_balance INTEGER;
    calculated_balance INTEGER;
BEGIN
    SELECT credits_balance INTO stored_balance
    FROM users WHERE id = user_id_param;
    
    SELECT COALESCE(SUM(delta_credits), 0) INTO calculated_balance
    FROM credit_transactions WHERE user_id = user_id_param;
    
    RETURN stored_balance = calculated_balance;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update user credit balance
CREATE OR REPLACE FUNCTION update_user_credit_balance()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users
    SET credits_balance = (
        SELECT COALESCE(SUM(delta_credits), 0)
        FROM credit_transactions
        WHERE user_id = NEW.user_id
    ),
    updated_at = NOW()
    WHERE id = NEW.user_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic balance updates
DROP TRIGGER IF EXISTS trigger_update_credit_balance ON credit_transactions;
CREATE TRIGGER trigger_update_credit_balance
    AFTER INSERT OR UPDATE OR DELETE ON credit_transactions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_credit_balance();

-- Analytics view for credit purchases
CREATE OR REPLACE VIEW credit_purchase_analytics AS
SELECT 
    DATE(created_at) as purchase_date,
    COUNT(*) as purchase_count,
    SUM(delta_credits) as total_credits_purchased,
    AVG(delta_credits) as avg_credits_per_purchase,
    SUM(CASE WHEN meta->>'package_name' = 'Starter Pack' THEN 1 ELSE 0 END) as starter_purchases,
    SUM(CASE WHEN meta->>'package_name' = 'Pro Pack' THEN 1 ELSE 0 END) as pro_purchases,
    SUM(CASE WHEN meta->>'package_name' = 'Premium Pack' THEN 1 ELSE 0 END) as premium_purchases
FROM credit_transactions
WHERE reason = 'purchase'
GROUP BY DATE(created_at)
ORDER BY purchase_date DESC;

-- Analytics view for credit usage by feature
CREATE OR REPLACE VIEW credit_usage_by_feature AS
SELECT 
    reason,
    COUNT(*) as usage_count,
    SUM(ABS(delta_credits)) as total_credits_spent,
    AVG(ABS(delta_credits)) as avg_credits_per_use,
    DATE(MIN(created_at)) as first_used,
    DATE(MAX(created_at)) as last_used
FROM credit_transactions
WHERE delta_credits < 0
GROUP BY reason
ORDER BY total_credits_spent DESC;

-- Analytics view for user credit segments
CREATE OR REPLACE VIEW user_credit_segments AS
SELECT 
    CASE 
        WHEN credits_balance = 0 THEN 'No Credits'
        WHEN credits_balance < 50 THEN 'Low Credits (1-49)'
        WHEN credits_balance < 200 THEN 'Medium Credits (50-199)'
        WHEN credits_balance < 500 THEN 'High Credits (200-499)'
        ELSE 'Very High Credits (500+)'
    END as credit_segment,
    COUNT(*) as user_count,
    AVG(credits_balance) as avg_balance,
    MIN(credits_balance) as min_balance,
    MAX(credits_balance) as max_balance
FROM users
WHERE credits_balance IS NOT NULL
GROUP BY 
    CASE 
        WHEN credits_balance = 0 THEN 'No Credits'
        WHEN credits_balance < 50 THEN 'Low Credits (1-49)'
        WHEN credits_balance < 200 THEN 'Medium Credits (50-199)'
        WHEN credits_balance < 500 THEN 'High Credits (200-499)'
        ELSE 'Very High Credits (500+)'
    END
ORDER BY MIN(credits_balance);

-- Grant permissions (adjust as needed for your setup)
GRANT SELECT ON credit_purchase_analytics TO PUBLIC;
GRANT SELECT ON credit_usage_by_feature TO PUBLIC;
GRANT SELECT ON user_credit_segments TO PUBLIC;
GRANT EXECUTE ON FUNCTION recalculate_user_credits(INTEGER) TO PUBLIC;
GRANT EXECUTE ON FUNCTION verify_credit_balance(INTEGER) TO PUBLIC;
