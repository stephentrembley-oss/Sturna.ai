"""Add evidence_packages table

Revision ID: 20260528_add_evidence_packages
Revises: 20260528_add_human_review_logs
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa


revision = '20260528_add_evidence_packages'
down_revision = '20260528_add_human_review_logs'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'evidence_packages',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('package_id', sa.String(length=64), nullable=False),
        sa.Column('framework', sa.String(length=50), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True)),
        sa.Column('period_end', sa.DateTime(timezone=True)),
        sa.Column('evidence_json', sa.JSON(), nullable=False),
        sa.Column('integrity_hash', sa.String(length=128), nullable=False),
        sa.Column('generated_by', sa.String(length=64)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_evidence_packages_package_id', 'evidence_packages', ['package_id'], unique=True)
    op.create_index('ix_evidence_packages_framework', 'evidence_packages', ['framework'])


def downgrade():
    op.drop_index('ix_evidence_packages_framework', table_name='evidence_packages')
    op.drop_index('ix_evidence_packages_package_id', table_name='evidence_packages')
    op.drop_table('evidence_packages')
