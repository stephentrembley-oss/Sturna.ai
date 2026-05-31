"""Demo and visitor models — Sturna.ai lead generation and nurture system.

Based on Polsia's:
•  migrations/1753000000000000_visitors_demo_sessions.js
•  migrations/1753200000000000_pilot_onboarding.js
•  src/cron/post-demo-nurture.js
•  email-templates/ (5 templates)

Tracks visitor journeys from first visit → demo → pilot → customer.
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class VisitorSource(PyEnum):
    """How the visitor discovered Sturna."""
    ORGANIC = "organic"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    PRODUCT_HUNT = "product_hunt"
    REFERRAL = "referral"
    DIRECT = "direct"
    EMAIL = "email"


class DemoStatus(PyEnum):
    """Demo session lifecycle."""
    STARTED = "started"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    CONVERTED = "converted"


class PilotStatus(PyEnum):
    """Pilot onboarding states."""
    INVITED = "invited"
    ACCEPTED = "accepted"
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    COMPLETED = "completed"
    CHURNED = "churned"


class NurtureStage(PyEnum):
    """Email nurture sequence stages."""
    NONE = "none"
    EMAIL_1_SENT = "email_1_sent"
    EMAIL_2_SENT = "email_2_sent"
    EMAIL_3_SENT = "email_3_sent"
    EMAIL_4_SENT = "email_4_sent"
    RESPONDED = "responded"
    CONVERTED = "converted"
    UNSUBSCRIBED = "unsubscribed"


class Visitor(Base):
    """Anonymous or identified visitor to Sturna.ai.
    Tracks every touchpoint for attribution and nurture triggering.
    """

    __tablename__ = "visitors"

    # Identification (may be anonymous initially)
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True
    )

    fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="Browser fingerprint for anonymous tracking"
    )

    # Attribution
    source: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=VisitorSource.ORGANIC.value,
        index=True
    )

    campaign: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="UTM campaign or internal campaign ID"
    )

    referrer: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True
    )

    landing_page: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    # Enrichment
    company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True
    )

    industry: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True
    )

    # Scoring
    lead_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="0-100 lead quality score"
    )

    is_qualified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    # Engagement
    page_views: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    session_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    last_seen_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Nurture state
    nurture_stage: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=NurtureStage.NONE.value
    )

    email1_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    email2_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    email3_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    email4_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Conversion
    demo_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    demo_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    pilot_purchased: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    pilot_purchased_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    stripe_customer_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True
    )

    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True
    )

    # Metadata (renamed from 'metadata' because it is reserved in SQLAlchemy Declarative)
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment="Page view history, click events, form submissions"
    )

    # Relationships
    demo_sessions: Mapped[List["DemoSession"]] = relationship(
        "DemoSession",
        back_populates="visitor",
        cascade="all, delete-orphan"
    )

    pilot: Mapped[Optional["PilotOnboarding"]] = relationship(
        "PilotOnboarding",
        back_populates="visitor",
        uselist=False
    )

    __table_args__ = (
        Index("ix_visitors_source_score", "source", "lead_score"),
        Index("ix_visitors_nurture", "nurture_stage", "demo_completed_at"),
        Index("ix_visitors_qualified", "is_qualified", "lead_score"),
    )


class DemoSession(Base):
    """A single demo session execution.
    Triggers the 3-email nurture sequence on completion.
    """

    __tablename__ = "demo_sessions"

    visitor_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("visitors.id"),
        nullable=False,
        index=True
    )

    session_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="agent_auction",
        comment="agent_auction, compliance_scan, vertical_demo"
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=DemoStatus.STARTED.value
    )

    # Execution
    intent_submitted: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="The demo intent the user submitted"
    )

    result_delivered: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Agent output shown to user"
    )

    execution_time_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )

    # Engagement
    agent_shown: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="Which agent won the demo auction"
    )

    transparency_card_viewed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    proof_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    # Conversion
    cta_clicked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    cta_type: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        comment="pilot_signup, pro_upgrade, schedule_call"
    )

    # Metadata (renamed from 'metadata' because it is reserved in SQLAlchemy Declarative)
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}"
    )

    # Relationships
    visitor: Mapped["Visitor"] = relationship("Visitor", back_populates="demo_sessions")

    __table_args__ = (
        Index("ix_demo_sessions_visitor_status", "visitor_id", "status"),
        Index("ix_demo_sessions_completed", "status", "created_at"),
    )


class PilotOnboarding(Base):
    """Pilot customer onboarding state machine.
    Tracks from purchase through white-glove setup to active usage.
    """

    __tablename__ = "pilot_onboarding"

    visitor_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("visitors.id"),
        unique=True,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=PilotStatus.INVITED.value
    )

    # Purchase
    plan: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="pilot",
        comment="pilot, pro, enterprise"
    )

    amount_paid: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    # Onboarding
    onboarding_data: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment="Compliance verticals, integrations, team size"
    )

    onboarding_status: Mapped[Dict[str, bool]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment="Step-by-step completion flags"
    )

    white_glove_purchased: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    white_glove_purchased_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Workspace
    workspace_name: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True
    )

    workspace_url: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    api_key_issued: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    api_key: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True
    )

    # Health
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    intents_processed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    # Recovery
    churn_risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    recovery_email_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    # Relationships
    visitor: Mapped["Visitor"] = relationship("Visitor", back_populates="pilot")

    __table_args__ = (
        Index("ix_pilot_status", "status"),
        Index("ix_pilot_white_glove", "white_glove_purchased"),
    )