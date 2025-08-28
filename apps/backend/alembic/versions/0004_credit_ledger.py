"""credit ledger schema

Revision ID: 0004_credit_ledger
Revises: 0003_add_performance_indexes
Create Date: 2025-08-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0004_credit_ledger'
down_revision: Union[str, None] = '0003_add_performance_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # stripe_customers (idempotent)
    if 'stripe_customers' not in insp.get_table_names():
        op.create_table(
            'stripe_customers',
            sa.Column('clerk_user_id', sa.Text(), nullable=False),
            sa.Column('stripe_customer_id', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('clerk_user_id'),
            sa.UniqueConstraint('stripe_customer_id', name='ux_stripe_customers_customer_id')
        )

    # credit_ledger (idempotent)
    if 'credit_ledger' not in insp.get_table_names():
        op.create_table(
            'credit_ledger',
            sa.Column('id', sa.BigInteger().with_variant(sa.BigInteger(), 'postgresql'), nullable=False),
            sa.Column('clerk_user_id', sa.Text(), nullable=False),
            sa.Column('delta', sa.Integer(), nullable=False),
            sa.Column('reason', sa.Text(), nullable=False),
            sa.Column('stripe_event_id', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['clerk_user_id'], ['stripe_customers.clerk_user_id'], name='fk_credit_ledger_user', ondelete='RESTRICT'),
            sa.PrimaryKeyConstraint('id')
        )
        # Use identity for Postgres if not already identity
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'credit_ledger'
                      AND column_name = 'id'
                      AND is_identity = 'YES'
                ) AND EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'credit_ledger'
                      AND column_name = 'id'
                      AND (column_default IS NULL OR column_default = '')
                ) THEN
                    EXECUTE 'ALTER TABLE credit_ledger ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY';
                END IF;
            END$$;
            """
        )
    else:
        # Ensure identity on existing table (best-effort, conditional)
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'credit_ledger'
                      AND column_name = 'id'
                      AND is_identity = 'YES'
                ) AND EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'credit_ledger'
                      AND column_name = 'id'
                      AND (column_default IS NULL OR column_default = '')
                ) THEN
                    EXECUTE 'ALTER TABLE credit_ledger ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY';
                END IF;
            END$$;
            """
        )

    # If historical duplicates exist for stripe_event_id (from runs before this migration),
    # remove duplicates keeping the smallest id so the unique index can be created.
    op.execute(
        """
        WITH d AS (
            SELECT stripe_event_id, MIN(id) AS keep_id
            FROM credit_ledger
            WHERE stripe_event_id IS NOT NULL
            GROUP BY stripe_event_id
            HAVING COUNT(*) > 1
        )
        DELETE FROM credit_ledger cl
        USING d
        WHERE cl.stripe_event_id = d.stripe_event_id
          AND cl.id <> d.keep_id;
        """
    )

    # Indexes (use IF NOT EXISTS via raw SQL for idempotency)
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_credit_ledger_stripe_event_id ON credit_ledger(stripe_event_id) WHERE stripe_event_id IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_credit_ledger_user ON credit_ledger(clerk_user_id)"
    )

    # View for balances (replace to be idempotent)
    op.execute(
        """
        CREATE OR REPLACE VIEW v_credit_balance AS
        SELECT clerk_user_id, COALESCE(SUM(delta), 0) AS balance
        FROM credit_ledger
        GROUP BY clerk_user_id;
        """
    )


def downgrade() -> None:
    # Drop view first due to dependency
    op.execute("DROP VIEW IF EXISTS v_credit_balance")

    op.drop_index('ix_credit_ledger_user', table_name='credit_ledger')
    op.drop_index('ux_credit_ledger_stripe_event_id', table_name='credit_ledger')
    op.drop_table('credit_ledger')
    op.drop_table('stripe_customers')
