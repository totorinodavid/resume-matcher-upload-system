"""Production credit system tables

Revision ID: 0006_production_credits
Revises: 0005_file_uploads
Create Date: 2025-09-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0006_production_credits'
down_revision = '0005_file_uploads'
branch_labels = None
depends_on = None


def upgrade():
    # Create payment status enum
    payment_status_enum = sa.Enum(
        'INIT', 'PAID', 'CREDITED', 'REFUNDED', 'CHARGEBACK', 'CANCELED', 'FAILED',
        name='payment_status'
    )
    payment_status_enum.create(op.get_bind())
    
    # Add credits_balance to users table if it doesn't exist
    try:
        op.add_column('users', sa.Column('credits_balance', sa.Integer(), nullable=False, server_default='0'))
    except Exception:
        # Column might already exist from manual addition
        pass
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('provider_checkout_session_id', sa.String(length=255), nullable=True),
        sa.Column('amount_total_cents', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('expected_credits', sa.Integer(), nullable=False),
        sa.Column('status', payment_status_enum, nullable=False),
        sa.Column('raw_provider_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('amount_total_cents >= 0', name='ck_amount_positive'),
        sa.CheckConstraint('expected_credits >= 0', name='ck_credits_positive'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_payment_intent_id', name='uq_provider_pi'),
        sa.UniqueConstraint('provider', 'provider_checkout_session_id', name='uq_provider_cs')
    )
    
    # Create indexes for payments
    op.create_index('idx_payments_user_id', 'payments', ['user_id'])
    op.create_index('idx_payments_status', 'payments', ['status'])
    op.create_index('idx_payments_created_at', 'payments', ['created_at'])
    
    # Create credit_transactions table
    op.create_table('credit_transactions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Text(), nullable=False),
        sa.Column('payment_id', sa.BigInteger(), nullable=True),
        sa.Column('admin_action_id', sa.BigInteger(), nullable=True),
        sa.Column('delta_credits', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for credit_transactions
    op.create_index('idx_credit_tx_user_id', 'credit_transactions', ['user_id'])
    op.create_index('idx_credit_tx_created_at', 'credit_transactions', ['created_at'])
    op.create_index('idx_credit_tx_payment_id', 'credit_transactions', ['payment_id'])
    
    # Create processed_events table for idempotency
    op.create_table('processed_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('provider_event_id', sa.String(length=255), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('payload_sha256', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('provider', 'provider_event_id', name='uq_provider_event')
    )
    
    # Create indexes for processed_events
    op.create_index('idx_processed_events_provider', 'processed_events', ['provider'])
    op.create_index('idx_processed_events_received_at', 'processed_events', ['received_at'])
    
    # Create admin_actions table
    op.create_table('admin_actions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('actor_user_id', sa.Text(), nullable=False),
        sa.Column('target_user_id', sa.Text(), nullable=False),
        sa.Column('delta_credits', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for admin_actions
    op.create_index('idx_admin_actions_actor', 'admin_actions', ['actor_user_id'])
    op.create_index('idx_admin_actions_target', 'admin_actions', ['target_user_id'])
    op.create_index('idx_admin_actions_created_at', 'admin_actions', ['created_at'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('admin_actions')
    op.drop_table('processed_events')
    op.drop_table('credit_transactions')
    op.drop_table('payments')
    
    # Drop enum
    payment_status_enum = sa.Enum(name='payment_status')
    payment_status_enum.drop(op.get_bind())
    
    # Remove credits_balance column from users (optional - might want to keep data)
    # op.drop_column('users', 'credits_balance')
