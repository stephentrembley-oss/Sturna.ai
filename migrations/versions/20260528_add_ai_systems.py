"""Add ai_systems table

Revision ID: 20260528_add_ai_systems
Revises: 20260528_add_evidence_packages
Create Date: 2026-05-28
"""
from alembic import op
import sqlalchemy as sa


revision = '20260528_add_ai_systems'
down_revision = '20260528_add_evidence_packages'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ai_systems',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('system_id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('owner', sa.String(length=64), nullable=False),
        sa.Column('eu_ai_act_high_risk', sa.Boolean(), default=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_ai_systems_system_id', 'ai_systems', ['system_id'], unique=True)
    op.create_index('ix_ai_systems_risk_level', 'ai_systems', ['risk_level'])


def downgrade():
    op.drop_index('ix_ai_systems_risk_level', table_name='ai_systems')
    op.drop_index('ix_ai_systems_system_id', table_name='ai_systems')
    op.drop_table('ai_systems')
