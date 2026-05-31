"""Add demo and visitor models.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Visitors
    op.create_table(
        "visitors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=True, index=True),
        sa.Column("fingerprint", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("source", sa.String(16), nullable=False, default="organic", index=True),
        sa.Column("campaign", sa.String(64), nullable=True),
        sa.Column("referrer", sa.String(512), nullable=True),
        sa.Column("landing_page", sa.String(255), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("title", sa.String(128), nullable=True),
        sa.Column("industry", sa.String(64), nullable=True),
        sa.Column("lead_score", sa.Integer(), nullable=False, default=0),
        sa.Column("is_qualified", sa.Boolean(), nullable=False, default=False),
        sa.Column("page_views", sa.Integer(), nullable=False, default=0),
        sa.Column("session_count", sa.Integer(), nullable=False, default=0),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("nurture_stage", sa.String(16), nullable=False, default="none"),
        sa.Column("email1_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email2_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email3_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("email4_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("demo_completed", sa.Boolean(), nullable=False, default=False),
        sa.Column("demo_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pilot_purchased", sa.Boolean(), nullable=False, default=False),
        sa.Column("pilot_purchased_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stripe_customer_id", sa.String(64), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(64), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_visitors_source_score", "visitors", ["source", "lead_score"])
    op.create_index("ix_visitors_nurture", "visitors", ["nurture_stage", "demo_completed_at"])
    op.create_index("ix_visitors_qualified", "visitors", ["is_qualified", "lead_score"])

    # Demo Sessions
    op.create_table(
        "demo_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("visitor_id", sa.String(64), sa.ForeignKey("visitors.id"), nullable=False, index=True),
        sa.Column("session_type", sa.String(32), nullable=False, default="agent_auction"),
        sa.Column("status", sa.String(16), nullable=False, default="started"),
        sa.Column("intent_submitted", sa.Text(), nullable=True),
        sa.Column("result_delivered", sa.Text(), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=True),
        sa.Column("agent_shown", sa.String(64), nullable=True),
        sa.Column("transparency_card_viewed", sa.Boolean(), nullable=False, default=False),
        sa.Column("proof_verified", sa.Boolean(), nullable=False, default=False),
        sa.Column("cta_clicked", sa.Boolean(), nullable=False, default=False),
        sa.Column("cta_type", sa.String(32), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_demo_sessions_visitor_status", "demo_sessions", ["visitor_id", "status"])
    op.create_index("ix_demo_sessions_completed", "demo_sessions", ["status", "created_at"])

    # Pilot Onboarding
    op.create_table(
        "pilot_onboarding",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("visitor_id", sa.String(64), sa.ForeignKey("visitors.id"), unique=True, nullable=False),
        sa.Column("status", sa.String(16), nullable=False, default="invited"),
        sa.Column("plan", sa.String(16), nullable=False, default="pilot"),
        sa.Column("amount_paid", sa.Float(), nullable=False, default=0.0),
        sa.Column("onboarding_data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("onboarding_status", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("white_glove_purchased", sa.Boolean(), nullable=False, default=False),
        sa.Column("white_glove_purchased_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workspace_name", sa.String(128), nullable=True),
        sa.Column("workspace_url", sa.String(255), nullable=True),
        sa.Column("api_key_issued", sa.Boolean(), nullable=False, default=False),
        sa.Column("api_key", sa.String(64), nullable=True),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("intents_processed", sa.Integer(), nullable=False, default=0),
        sa.Column("churn_risk_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("recovery_email_sent", sa.Boolean(), nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_pilot_status", "pilot_onboarding", ["status"])
    op.create_index("ix_pilot_white_glove", "pilot_onboarding", ["white_glove_purchased"])


def downgrade() -> None:
    op.drop_table("pilot_onboarding")
    op.drop_table("demo_sessions")
    op.drop_table("visitors")