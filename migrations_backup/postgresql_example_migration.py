"""Add PostgreSQL-specific features to resume tables

Revision ID: postgresql_features_001
Revises: previous_migration
Create Date: 2025-08-29 12:00:00.000000

PostgreSQL-specific improvements:
- JSONB columns for flexible data storage
- Full-text search indexes
- Advanced constraints and triggers
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = 'postgresql_features_001'
down_revision = None  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add PostgreSQL-specific features to resume tables."""
    
    # Create users table with JSONB metadata
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False, default=0),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Create resumes table with JSONB structured data
    op.create_table(
        'resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('structured_data', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('skills', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('keywords', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create jobs table with JSONB requirements
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requirements', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('skills_required', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create match results table with JSONB analysis
    op.create_table(
        'match_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('analysis', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('missing_skills', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('matching_skills', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE')
    )
    
    # PostgreSQL-specific indexes for performance
    
    # JSONB GIN indexes for fast queries
    op.create_index('idx_users_metadata_gin', 'users', ['metadata'], postgresql_using='gin')
    op.create_index('idx_resumes_structured_data_gin', 'resumes', ['structured_data'], postgresql_using='gin')
    op.create_index('idx_resumes_skills_gin', 'resumes', ['skills'], postgresql_using='gin')
    op.create_index('idx_jobs_requirements_gin', 'jobs', ['requirements'], postgresql_using='gin')
    op.create_index('idx_jobs_skills_required_gin', 'jobs', ['skills_required'], postgresql_using='gin')
    op.create_index('idx_match_analysis_gin', 'match_results', ['analysis'], postgresql_using='gin')
    
    # B-tree indexes for common queries
    op.create_index('idx_resumes_user_id_status', 'resumes', ['user_id', 'status'])
    op.create_index('idx_jobs_user_id_created', 'jobs', ['user_id', 'created_at'])
    op.create_index('idx_match_score_desc', 'match_results', [sa.text('score DESC')])
    
    # Full-text search indexes
    op.create_index(
        'idx_resumes_content_fts',
        'resumes',
        [sa.text("to_tsvector('english', content)")],
        postgresql_using='gin'
    )
    op.create_index(
        'idx_jobs_description_fts', 
        'jobs',
        [sa.text("to_tsvector('english', description)")],
        postgresql_using='gin'
    )
    
    # PostgreSQL constraints and triggers
    
    # Check constraints
    op.create_check_constraint(
        'ck_users_credits_positive',
        'users', 
        sa.text('credits >= 0')
    )
    op.create_check_constraint(
        'ck_match_score_valid',
        'match_results',
        sa.text('score >= 0 AND score <= 1')
    )
    
    # Create trigger function for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create triggers for automatic updated_at
    for table in ['users', 'resumes', 'jobs']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)


def downgrade() -> None:
    """Remove PostgreSQL-specific features."""
    
    # Drop triggers
    for table in ['users', 'resumes', 'jobs']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}")
    
    # Drop trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    
    # Drop indexes
    op.drop_index('idx_jobs_description_fts', 'jobs')
    op.drop_index('idx_resumes_content_fts', 'resumes')
    op.drop_index('idx_match_score_desc', 'match_results')
    op.drop_index('idx_jobs_user_id_created', 'jobs')
    op.drop_index('idx_resumes_user_id_status', 'resumes')
    op.drop_index('idx_match_analysis_gin', 'match_results')
    op.drop_index('idx_jobs_skills_required_gin', 'jobs')
    op.drop_index('idx_jobs_requirements_gin', 'jobs')
    op.drop_index('idx_resumes_skills_gin', 'resumes')
    op.drop_index('idx_resumes_structured_data_gin', 'resumes')
    op.drop_index('idx_users_metadata_gin', 'users')
    
    # Drop tables
    op.drop_table('match_results')
    op.drop_table('jobs')
    op.drop_table('resumes')
    op.drop_table('users')
