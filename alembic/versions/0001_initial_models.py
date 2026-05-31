"""Initial migration — Sturna.ai Phase 1 core schema.
Creates all tables for the multi-agent registry and hybrid memory system.

Revision ID: 001
Revises: 
Create Date: 2026-05-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================
    # AGENTS
    # ============================================
    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("agent_id", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("agent_class", sa.String(32), nullable=False, index=True),
        sa.Column("coalition", sa.String(32), nullable=True, index=True),
        sa.Column("capability_hash", sa.String(64), nullable=False),
        sa.Column("capabilities", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("swarm_score", sa.Integer(), nullable=False, default=0),
        sa.Column("tier", sa.String(16), nullable=False, default="bronze"),
        sa.Column("status", sa.String(16), nullable=False, default="active", index=True),
        sa.Column("health_score", sa.Float(), nullable=False, default=1.0),
        sa.Column("march_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("bid_confidence", sa.Float(), nullable=False, default=0.5),
        sa.Column("success_rate", sa.Float(), nullable=False, default=0.0),
        sa.Column("avg_latency_ms", sa.Float(), nullable=False, default=0.0),
        sa.Column("cost_per_intent", sa.Float(), nullable=False, default=0.0),
        sa.Column("model_endpoint", sa.String(512), nullable=True),
        sa.Column("model_name", sa.String(64), nullable=True),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quarantined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quarantine_reason", sa.Text(), nullable=True),
    )
    op.create_index("ix_agents_coalition_status", "agents", ["coalition", "status"])
    op.create_index("ix_agents_tier_score", "agents", ["tier", "swarm_score"])
    op.create_index("ix_agents_class_health", "agents", ["agent_class", "health_score"])

    # Agent Identity Registry (ERC-8004)
    op.create_table(
        "agent_identity_registry",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("agent_id", sa.String(64), sa.ForeignKey("agents.agent_id"), unique=True, nullable=False, index=True),
        sa.Column("token_id", sa.String(64), unique=True, nullable=False),
        sa.Column("reputation_history", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("registered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # ============================================
    # MEMORIES
    # ============================================
    op.create_table(
        "agent_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("agent_id", sa.String(64), sa.ForeignKey("agents.agent_id"), nullable=False, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("tier", sa.String(16), nullable=False, default="recall", index=True),
        sa.Column("memory_type", sa.String(32), nullable=False, default="intent_pattern", index=True),
        sa.Column("status", sa.String(16), nullable=False, default="active", index=True),
        sa.Column("verification_score", sa.Float(), nullable=False, default=0.0),
        sa.Column("gsar_pass", sa.Boolean(), nullable=False, default=False),
        sa.Column("grounding_source", sa.String(512), nullable=True),
        sa.Column("session_id", sa.String(64), nullable=True, index=True),
        sa.Column("intent_id", sa.String(64), nullable=True, index=True),
        sa.Column("decay_factor", sa.Float(), nullable=False, default=1.0),
        sa.Column("access_count", sa.Integer(), nullable=False, default=0),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("parent_memory_ids", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("child_memory_ids", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_memories_agent_tier", "agent_memories", ["agent_id", "tier"])
    op.create_index("ix_memories_agent_type", "agent_memories", ["agent_id", "memory_type"])
    op.create_index("ix_memories_status_decay", "agent_memories", ["status", "decay_factor"])
    op.create_index("ix_memories_session", "agent_memories", ["session_id"])

    # Shared Memories
    op.create_table(
        "shared_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("pattern_id", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("category", sa.String(32), nullable=False, index=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("source_agent_ids", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("source_memory_ids", postgresql.ARRAY(sa.String()), nullable=False, server_default="{}"),
        sa.Column("confidence", sa.Float(), nullable=False, default=0.0),
        sa.Column("frequency", sa.Integer(), nullable=False, default=1),
        sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    op.create_index("ix_shared_category_confidence", "shared_memories", ["category", "confidence"])

    # Memory Defense Logs
    op.create_table(
        "memory_defense_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("memory_id", sa.String(64), sa.ForeignKey("agent_memories.id"), nullable=False, index=True),
        sa.Column("probe_type", sa.String(32), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("action_taken", sa.String(32), nullable=False, default="quarantined"),
        sa.Column("evidence", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    # Drop in reverse order to respect FK constraints
    op.drop_table("memory_defense_logs")
    op.drop_table("shared_memories")
    op.drop_table("agent_memories")
    op.drop_table("agent_identity_registry")
    op.drop_table("agents")