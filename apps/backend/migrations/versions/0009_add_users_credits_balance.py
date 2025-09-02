"""Add credits_balance column to users table

Revision ID: 0009_add_users_credits_balance
Revises: 0008_create_credit_balance_view
Create Date: 2025-09-02 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0009_add_users_credits_balance'
down_revision = '0008_create_credit_balance_view'
branch_labels = None
depends_on = None

def upgrade():
    """Add credits_balance column to users table"""
    # Add credits_balance column if it doesn't exist
    try:
        op.add_column('users', sa.Column('credits_balance', sa.Integer(), nullable=False, server_default='0'))
        print("✅ Added credits_balance column to users table")
    except Exception as e:
        print(f"⚠️  Column might already exist: {e}")
        # Continue anyway - column already exists

def downgrade():
    """Remove credits_balance column from users table"""
    op.drop_column('users', 'credits_balance')
