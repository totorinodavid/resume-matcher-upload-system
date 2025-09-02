"""Create v_credit_balance view

Revision ID: 0008_create_credit_balance_view
Revises: 0007_bulletproof_credits
Create Date: 2025-09-02 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0008_create_credit_balance_view'
down_revision = '0007_bulletproof_credits'
branch_labels = None
depends_on = None

def upgrade():
    """Create the v_credit_balance view"""
    op.execute("""
        CREATE OR REPLACE VIEW v_credit_balance AS
        SELECT 
            user_id,
            COALESCE(SUM(delta), 0) AS balance
        FROM credit_ledger
        GROUP BY user_id;
    """)

def downgrade():
    """Drop the v_credit_balance view"""
    op.execute("DROP VIEW IF EXISTS v_credit_balance;")
