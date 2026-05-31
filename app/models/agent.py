"""Agent model — Sturna.ai multi-agent registry.
Based on Polsia's:
•  services/agent-contract-service.js (ERC-8004 agent registry)
•  migrations/1710000000000_agent_registry.js
•  whitepapers/ERC8004-AgentIdentity.sol
Each agent is a specialist that competes in Coalition Market Auctions.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class AgentTier(PyEnum):
    """ERC-8004 SwarmScore tier system."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class AgentStatus(PyEnum):
    """Agent lifecycle states."""
    ACTIVE = "active"
    QUARANTINED = "quarantined"
    DEPRECATED = "deprecated"
    TRAINING = "training"


class AgentClass(PyEnum):
    """Agent specialization classes for coalition grouping."""
    FINANCIAL_ANALYSIS = "financial_analysis"
    TECHNICAL_AUDIT = "technical_audit"
    CONTENT_STRATEGY = "content_strategy"
    RESEARCH_SYNTHESIS = "research_synthesis"
    LEGAL_COMPLIANCE = "legal_compliance"
    MEDICAL_REVIEW = "medical_review"
    SUPPLY_CHAIN = "supply_chain"
    TRADING_QUANT = "trading_quant"


class Agent(Base):
    """Specialist agent registered for Coalition Market Auctions."""

    __tablename__ = "agents"

    # Identity
    agent_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
        comment="ERC-8004 agent identifier"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable agent name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Agent capability description"
    )

    # Classification
    agent_class: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="Specialization class for coalition routing"
    )

    coalition: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        index=True,
        comment="Assigned coalition (financial-analysis, etc.)"
    )

    # Capability fingerprint (immutable)
    capability_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash of agent capability manifest"
    )

    capabilities: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
        comment="List of capability tags"
    )

    # Reputation system
    swarm_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="ERC-8004 SwarmScore V2 (0-1000 scale)"
    )

    tier: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AgentTier.BRONZE.value,
        comment="Reputation tier"
    )

    # Health & status
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AgentStatus.ACTIVE.value,
        index=True,
        comment="Current lifecycle state"
    )

    health_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="IML drift health score (0.0-1.0)"
    )

    march_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="MARCH quality gate score (0-100)"
    )

    # Bidding & routing
    bid_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        comment="Current bidding confidence (0.0-1.0)"
    )

    success_rate: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Historical first-pass success rate"
    )

    avg_latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Average execution latency in milliseconds"
    )

    # Cost tracking
    cost_per_intent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Average cost per intent execution ($ )"
    )

    # Metadata
    model_endpoint: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="LLM endpoint URL (OpenAI, Anthropic, etc.)"
    )

    model_name: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="Model identifier (gpt-4o, claude-3-5-sonnet, etc.)"
    )

    config: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment="Agent-specific configuration"
    )

    # Timestamps (inherited from Base)
    last_active_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time agent executed an intent"
    )

    quarantined_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When agent was quarantined (if applicable)"
    )

    quarantine_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Reason for quarantine"
    )

    # Relationships
    memories: Mapped[List["AgentMemory"]] = relationship(
        "AgentMemory",
        back_populates="agent",
        cascade="all, delete-orphan"
    )

    bids: Mapped[List["AuctionBid"]] = relationship(
        "AuctionBid",
        back_populates="agent",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_agents_coalition_status", "coalition", "status"),
        Index("ix_agents_tier_score", "tier", "swarm_score"),
        Index("ix_agents_class_health", "agent_class", "health_score"),
    )


class AgentIdentityRegistry(Base):
    """ERC-8004 compliant soulbound token registry."""

    __tablename__ = "agent_identity_registry"

    agent_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("agents.agent_id"),
        unique=True,
        nullable=False,
        index=True
    )

    token_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        comment="ERC-8004 soulbound token ID"
    )

    reputation_history: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="[]",
        comment="Append-only reputation events"
    )

    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    agent: Mapped["Agent"] = relationship("Agent")