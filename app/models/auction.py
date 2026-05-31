"""Auction model — Sturna.ai Coalition Market Auction system.

VCG-style sealed-bid auction for multi-agent intent execution.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, Dict, Any

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AuctionStatus(PyEnum):
    """Lifecycle states of an auction."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BidStatus(PyEnum):
    """Individual bid states."""
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    SHORTLISTED = "shortlisted"
    WON = "won"
    LOST = "lost"


class Auction(Base):
    """A Coalition Market Auction for a single intent."""

    __tablename__ = "auctions"

    intent_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Link to the intent that triggered this auction"
    )

    intent_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Original intent text submitted by user"
    )

    intent_category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="financial, legal, medical, technical, etc."
    )

    coalition: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="Which coalition of agents competed (e.g. financial, compliance)"
    )

    eligible_agent_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="How many agents were eligible to bid"
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=AuctionStatus.PENDING.value,
        index=True,
    )

    # Winner information
    winner_agent_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("agents.agent_id"),
        nullable=True,
        index=True,
    )

    winner_bid_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    winner_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    vcg_price: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="VCG payment price (second-price auction)"
    )

    execution_time_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    result_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Final output from the winning agent (real LLM result)"
    )

    result_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    verification_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    march_passed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    compliance_flags: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    proof_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        unique=True,
        nullable=True,
    )

    proof_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pending",
    )

    proof_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )

    transparency_card: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
    )

    # Metadata (using 'meta' to avoid SQLAlchemy reserved word)
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_auctions_status_coalition", "status", "coalition"),
        Index("ix_auctions_intent_category", "intent_category"),
        Index("ix_auctions_winner", "winner_agent_id"),
    )


class AuctionBid(Base):
    """Sealed bid submitted by an agent in an auction."""

    __tablename__ = "auction_bids"

    auction_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("auctions.id"),
        nullable=False,
        index=True,
    )

    agent_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("agents.agent_id"),
        nullable=False,
        index=True,
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Agent's self-reported confidence in executing the intent"
    )

    estimated_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    estimated_latency_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    capability_match_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=BidStatus.SUBMITTED.value,
    )

    encrypted_payload: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    vcg_payment: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    execution_result: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    execution_time_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Metadata (using 'meta' to avoid SQLAlchemy reserved word)
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    __table_args__ = (
        Index("ix_bids_auction_agent", "auction_id", "agent_id"),
        Index("ix_bids_confidence", "confidence_score"),
    )
