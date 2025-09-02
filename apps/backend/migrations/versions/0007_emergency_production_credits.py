"""Production Credits Migration - Emergency Fix
Revision ID: 0007_emergency_production_credits
Revises: 
Create Date: 2025-01-09 10:17:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '0007_emergency_production_credits'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Emergency production credits system migration"""
    
    # Create payment status enum
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentstatus') THEN
                CREATE TYPE paymentstatus AS ENUM ('pending', 'completed', 'failed', 'cancelled', 'refunded');
            END IF;
        END $$;
    """)
    
    # Add credits_balance to users table if not exists
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'credits_balance'
            ) THEN
                ALTER TABLE users ADD COLUMN credits_balance INTEGER DEFAULT 0 NOT NULL;
            END IF;
        END $$;
    """)
    
    # Fix payments table structure
    op.execute("""
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
    """)
    
    # Create stripe_customers table
    op.execute("""
        CREATE TABLE IF NOT EXISTS stripe_customers (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            stripe_customer_id VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create credit_transactions table
    op.execute("""
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
        )
    """)
    
    # Create processed_events table
    op.execute("""
        CREATE TABLE IF NOT EXISTS processed_events (
            id SERIAL PRIMARY KEY,
            event_id VARCHAR(255) UNIQUE NOT NULL,
            event_type VARCHAR(100) NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB
        )
    """)
    
    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_processed_events_event_id ON processed_events(event_id)")
    
    # Create stripe_session_id index only if column exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'payments' AND column_name = 'stripe_session_id'
            ) THEN
                CREATE INDEX IF NOT EXISTS idx_payments_stripe_session ON payments(stripe_session_id);
            END IF;
        END $$;
    """)
    
    # Add unique constraint on stripe_session_id
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE table_name = 'payments' 
                AND constraint_name = 'payments_stripe_session_id_unique'
            ) THEN
                -- Only if column exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'payments' AND column_name = 'stripe_session_id'
                ) THEN
                    ALTER TABLE payments ADD CONSTRAINT payments_stripe_session_id_unique UNIQUE (stripe_session_id);
                END IF;
            END IF;
        END $$;
    """)

def downgrade() -> None:
    """Downgrade migration"""
    # Drop tables created in this migration
    op.drop_table('processed_events', if_exists=True)
    op.drop_table('credit_transactions', if_exists=True) 
    op.drop_table('stripe_customers', if_exists=True)
    
    # Remove columns added to payments table
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS metadata")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS credits_granted")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS currency")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS stripe_payment_intent_id")
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS stripe_session_id")
    
    # Remove credits_balance from users
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS credits_balance")
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS paymentstatus")
