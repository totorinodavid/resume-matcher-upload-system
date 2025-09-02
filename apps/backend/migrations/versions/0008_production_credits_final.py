"""Add credits system tables and columns

Revision ID: 0008_production_credits_final
Revises: 
Create Date: 2025-09-02 10:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '0008_production_credits_final'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Upgrade database schema"""
    
    # 1. Add credits_balance to users table
    op.add_column('users', sa.Column('credits_balance', sa.Integer(), nullable=False, server_default='0'))
    
    # 2. Create payment status enum
    payment_status = postgresql.ENUM('pending', 'completed', 'failed', 'cancelled', 'refunded', name='paymentstatus')
    payment_status.create(op.get_bind(), checkfirst=True)
    
    # 3. Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_session_id', sa.String(255), nullable=True),
        sa.Column('stripe_payment_intent_id', sa.String(255), nullable=True),
        sa.Column('amount_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=True, server_default='usd'),
        sa.Column('status', postgresql.ENUM('pending', 'completed', 'failed', 'cancelled', 'refunded', name='paymentstatus'), nullable=True, server_default='pending'),
        sa.Column('credits_granted', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_session_id')
    )
    
    # 4. Create stripe_customers table
    op.create_table(
        'stripe_customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_customer_id')
    )
    
    # 5. Create credit_transactions table
    op.create_table(
        'credit_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('balance_before', sa.Integer(), nullable=False),
        sa.Column('balance_after', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 6. Create processed_events table
    op.create_table(
        'processed_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.String(255), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )
    
    # 7. Create indexes
    op.create_index('idx_payments_user_id', 'payments', ['user_id'])
    op.create_index('idx_payments_stripe_session', 'payments', ['stripe_session_id'])
    op.create_index('idx_credit_transactions_user_id', 'credit_transactions', ['user_id'])
    op.create_index('idx_processed_events_event_id', 'processed_events', ['event_id'])

def downgrade() -> None:
    """Downgrade database schema"""
    # Drop indexes
    op.drop_index('idx_processed_events_event_id', 'processed_events')
    op.drop_index('idx_credit_transactions_user_id', 'credit_transactions')
    op.drop_index('idx_payments_stripe_session', 'payments')
    op.drop_index('idx_payments_user_id', 'payments')
    
    # Drop tables
    op.drop_table('processed_events')
    op.drop_table('credit_transactions')
    op.drop_table('stripe_customers')
    op.drop_table('payments')
    
    # Drop enum
    payment_status = postgresql.ENUM('pending', 'completed', 'failed', 'cancelled', 'refunded', name='paymentstatus')
    payment_status.drop(op.get_bind())
    
    # Drop column
    op.drop_column('users', 'credits_balance')
