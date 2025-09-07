"""File uploads table

Revision ID: 0005_file_uploads
Revises: 0004_credit_ledger
Create Date: 2025-08-29
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0005_file_uploads'
down_revision: Union[str, None] = '0004_credit_ledger'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create file_uploads table
    op.create_table(
        'file_uploads',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('storage_url', sa.Text(), nullable=False),
        sa.Column('storage_key', sa.String(), nullable=True),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_hash', sa.String(), nullable=True),
        sa.Column('processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('resume_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('ix_file_uploads_user_id', 'file_uploads', ['user_id'])
    op.create_index('ix_file_uploads_file_hash', 'file_uploads', ['file_hash'])
    op.create_index('ix_file_uploads_created_at', 'file_uploads', ['created_at'])
    op.create_index('ix_file_uploads_processed', 'file_uploads', ['processed'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_file_uploads_processed', 'file_uploads')
    op.drop_index('ix_file_uploads_created_at', 'file_uploads')
    op.drop_index('ix_file_uploads_file_hash', 'file_uploads')
    op.drop_index('ix_file_uploads_user_id', 'file_uploads')
    
    # Drop table
    op.drop_table('file_uploads')
