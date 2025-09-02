"""Add StripeEvent table and improve users constraints

Revision ID: 0010_add_stripe_events_and_constraints
Revises: 0009_add_users_credits_balance
Create Date: 2025-09-02 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0010_add_stripe_events_and_constraints'
down_revision = '0009_add_users_credits_balance'
branch_labels = None
depends_on = None

def upgrade():
    """Add StripeEvent table and improve users table constraints"""
    
    # 1. Create stripe_events table for webhook deduplication
    op.create_table('stripe_events',
        sa.Column('event_id', sa.String(length=255), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('raw_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('processing_status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('event_id'),
    )
    
    # Add indexes for stripe_events
    op.create_index('ix_stripe_events_event_id', 'stripe_events', ['event_id'], unique=False)
    op.create_index('ix_stripe_events_event_type', 'stripe_events', ['event_type'], unique=False)
    
    # 2. Ensure users table has proper constraints
    # Add CHECK constraint for non-negative credits (if not exists)
    try:
        op.create_check_constraint(
            "credits_balance_nonneg",
            "users", 
            sa.text("credits_balance >= 0")
        )
        print("✅ Added credits_balance non-negative constraint")
    except Exception as e:
        print(f"⚠️  Credits constraint might already exist: {e}")
    
    # Ensure email index exists (if not exists)
    try:
        op.create_index("idx_users_email", "users", ["email"], unique=False)
        print("✅ Added email index to users table")
    except Exception as e:
        print(f"⚠️  Email index might already exist: {e}")
    
    # 3. Add credits_balance column if somehow missing
    try:
        op.add_column("users", sa.Column("credits_balance", sa.Integer(), nullable=False, server_default="0"))
        print("✅ Added credits_balance column")
    except Exception as e:
        print(f"⚠️  Credits column might already exist: {e}")


def downgrade():
    """Remove StripeEvent table and constraints"""
    
    # Remove stripe_events table
    op.drop_index('ix_stripe_events_event_type', table_name='stripe_events')
    op.drop_index('ix_stripe_events_event_id', table_name='stripe_events') 
    op.drop_table('stripe_events')
    
    # Remove constraints (optional - leave for safety)
    # op.drop_constraint("credits_balance_nonneg", "users", type_="check")
    # op.drop_index("idx_users_email", table_name="users")
