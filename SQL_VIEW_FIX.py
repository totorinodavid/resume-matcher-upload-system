#!/usr/bin/env python3
"""
EMERGENCY SQL VIEW FIX FOR RENDER DATABASE
Direct SQL commands to create missing v_credit_balance view
"""

# Direct SQL commands to run on Render database

VIEW_CREATION_SQL = """
-- Emergency fix for missing v_credit_balance view
-- Run this SQL directly on the database

CREATE OR REPLACE VIEW v_credit_balance AS
SELECT 
    user_id,
    COALESCE(SUM(delta), 0) AS balance
FROM credit_ledger
GROUP BY user_id;

-- Test the view
SELECT COUNT(*) as user_count FROM v_credit_balance;

-- Show some sample data
SELECT user_id, balance FROM v_credit_balance LIMIT 5;
"""

print("🚨 EMERGENCY DATABASE VIEW FIX")
print("=" * 50)
print()
print("❌ PROBLEM: relation 'v_credit_balance' does not exist")
print("🔧 SOLUTION: Create the missing view with this SQL:")
print()
print("📋 SQL TO RUN ON DATABASE:")
print("-" * 30)
print(VIEW_CREATION_SQL)
print("-" * 30)
print()
print("📝 INSTRUCTIONS:")
print("1. Connect to your Render PostgreSQL database")
print("2. Run the SQL commands above")
print("3. Verify the view is created")
print("4. The credits system should work immediately")
print()
print("🎯 This will fix the ERROR: relation 'v_credit_balance' does not exist")
