"""Add auction tables.

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-31
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create auctions table
    op.create_table(
        "auctions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("intent_id", sa.String(64), unique=True, nullable=False),
        sa.Column("intent_text", sa.Text(), nullable=False),
        sa.Column("intent_category", sa.String(32), nullable=False),
        sa.Column("coalition", sa.String(32), nullable=False),
        sa.Column("eligible_agent_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("winner_agent_id", sa.String(64), sa.ForeignKey("agents.agent_id"), nullable=True),
        sa.Column("winner_bid_id", sa.String(64), nullable=True),
        sa.Column("winner_confidence", sa.Float(), nullable=True),
        sa.Column("vcg_price", sa.Float(), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=True),
        sa.Column("result_content", sa.Text(), nullable=True),
        sa.Column("result_hash", sa.String(64), nullable=True),
        sa.Column("verification_score", sa.Float(), nullable=True),
        sa.Column("march_passed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("compliance_flags", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("proof_id", sa.String(64), unique=True, nullable=True),
        sa.Column("proof_status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("proof_data", postgresql.JSONB(), nullable=True),
        sa.Column("transparency_card", postgresql.JSONB(), nullable=True),
        sa.Column("meta", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_index("ix_auctions_status_coalition", "auctions", ["status", "coalition"])
    op.create_index("ix_auctions_intent_category", "auctions", ["intent_category"])
    op.create_index("ix_auctions_winner", "auctions", ["winner_agent_id"])

    # Create auction_bids table
    op.create_table(
        "auction_bids",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("auction_id", sa.String(64), sa.ForeignKey("auctions.id"), nullable=False),
        sa.Column("agent_id", sa.String(64), sa.ForeignKey("agents.agent_id"), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("estimated_cost", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("estimated_latency_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("capability_match_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("status", sa.String(16), nullable=False, server_default="submitted"),
        sa.Column("encrypted_payload", sa.Text(), nullable=True),
        sa.Column("vcg_payment", sa.Float(), nullable=True),
        sa.Column("execution_result", sa.Text(), nullable=True),
        sa.Column("execution_time_ms", sa.Float(), nullable=True),
        sa.Column("meta", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    op.create_index("ix_bids_auction_agent", "auction_bids", ["auction_id", "agent_id"])
    op.create_index("ix_bids_confidence", "auction_bids", ["confidence_score"])


def downgrade() -> None:
    op.drop_index("ix_bids_confidence", table_name="auction_bids")
    op.drop_index("ix_bids_auction_agent", table_name="auction_bids")
    op.drop_table("auction_bids")

    op.drop_index("ix_auctions_winner", table_name="auctions")
    op.drop_index("ix_auctions_intent_category", table_name="auctions")
    op.drop_index("ix_auctions_status_coalition", table_name="auctions")
    op.drop_table("auctions")
