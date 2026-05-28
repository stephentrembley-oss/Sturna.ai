"""Add human_review_logs table

Revision ID: 20260528_add_human_review_logs
Revises: 
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa


revision = '20260528_add_human_review_logs'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'human_review_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('decision_id', sa.String(length=64), nullable=False),
        sa.Column('task_id', sa.String(length=64), nullable=False),
        sa.Column('agent_id', sa.String(length=64), nullable=False),
        sa.Column('decision', sa.String(length=20), nullable=False),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('reviewer_id', sa.String(length=64), nullable=False),
        sa.Column('reviewer_role', sa.String(length=50), nullable=True),
        sa.Column('previous_decision_id', sa.String(length=64), nullable=True),
        sa.Column('chain_hash', sa.String(length=128), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('is_pending', sa.Boolean(), default=False),
    )
    op.create_index('ix_human_review_logs_decision_id', 'human_review_logs', ['decision_id'], unique=True)
    op.create_index('ix_human_review_logs_task_id', 'human_review_logs', ['task_id'])
    op.create_index('ix_human_review_logs_agent_id', 'human_review_logs', ['agent_id'])
    op.create_index('ix_human_review_logs_is_pending', 'human_review_logs', ['is_pending'])


def downgrade():
    op.drop_index('ix_human_review_logs_is_pending', table_name='human_review_logs')
    op.drop_index('ix_human_review_logs_agent_id', table_name='human_review_logs')
    op.drop_index('ix_human_review_logs_task_id', table_name='human_review_logs')
    op.drop_index('ix_human_review_logs_decision_id', table_name='human_review_logs')
    op.drop_table('human_review_logs')
