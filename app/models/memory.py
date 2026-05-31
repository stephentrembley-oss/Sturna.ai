"""Memory model — Sturna.ai hybrid vector-graph memory system.

Based on Polsia's:
- services/agent-memory-service.js (§7D Hybrid Memory)
- routes/agent-memory.js
- routes/memory-shared.js (§7B LangMem daemon output)
- routes/memory-defense.js (§16C Context Poisoning Defense)

Three tiers: recall (fast), episodic (session), semantic (compressed), core (permanent).
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MemoryTier(PyEnum):
    """Memory storage tiers with different retention and access patterns."""
    RECALL = "recall"        # Fast, recent, high-fidelity
    EPISODIC = "episodic"    # Session-scoped, temporal
    SEMANTIC = "semantic"    # Compressed, pattern-based
    CORE = "core"            # Permanent, identity-defining


class MemoryType(PyEnum):
    """Types of stored memory patterns."""
    INTENT_PATTERN = "intent_pattern"      # Successful intent execution
    ANTI_PATTERN = "anti_pattern"          # Failed / blocked patterns
    COALITION_INSIGHT = "coalition_insight"  # Cross-agent learnings
    FACTUAL_GROUNDING = "factual_grounding"  # Verified claims
    DOMAIN_KNOWLEDGE = "domain_knowledge"    # Injected product context
    ADAPTIVE_RULE = "adaptive_rule"          # Self-evolved heuristics


class MemoryStatus(PyEnum):
    """Memory lifecycle states."""
    ACTIVE = "active"
    ARCHIVED = "archived"      # Moved to cold storage
    QUARANTINED = "quarantined"  # Contamination detected
    INVALIDATED = "invalidated"  # Superseded by newer memory


class AgentMemory(Base):
    """Individual memory entry for an agent.
    
    Hybrid vector-graph storage:
    - Vector: semantic embedding for similarity search (pgvector)
    - Graph: edges link related memories (BFS traversable via parent/child IDs)
    - Metadata: tier, type, verification status, decay schedule
    """
    
    __tablename__ = "agent_memories"
    
    # Foreign key to agent
    agent_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("agents.agent_id"),
        nullable=False,
        index=True
    )
    
    # Content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Raw memory content (text, JSON, etc.)"
    )
    
    content_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 hash of content for deduplication"
    )
    
    # Vector embedding for semantic search (requires pgvector extension)
    # Use ARRAY(Float) as fallback; migrate to pgvector VECTOR(1536) when extension is enabled
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        ARRAY(Float),
        nullable=True,
        comment="OpenAI text-embedding-3-large (1536-dim) or compatible"
    )
    
    # Classification
    tier: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=MemoryTier.RECALL.value,
        index=True,
        comment="Storage tier: recall, episodic, semantic, core"
    )
    
    memory_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=MemoryType.INTENT_PATTERN.value,
        index=True,
        comment="Pattern type: intent, anti-pattern, coalition-insight, etc."
    )
    
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=MemoryStatus.ACTIVE.value,
        index=True,
        comment="Lifecycle: active, archived, quarantined, invalidated"
    )
    
    # Verification
    verification_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Triple-gate verification score (0-100)"
    )
    
    gsar_pass: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="GSAR four-way classification passed"
    )
    
    grounding_source: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
        comment="URL, document ID, or API source for factual grounding"
    )
    
    # Temporal scoping
    session_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="Episodic session scope"
    )
    
    intent_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="Associated intent execution ID"
    )
    
    # Decay & archival
    decay_factor: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
        comment="Retention priority (1.0 = permanent, 0.0 = ephemeral)"
    )
    
    access_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of times recalled"
    )
    
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Graph edges (stored as adjacency list for BFS traversal)
    parent_memory_ids: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
        comment="Upstream memory references"
    )
    
    child_memory_ids: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
        comment="Downstream memory references"
    )
    
    # Metadata (renamed from 'metadata' because it is reserved in SQLAlchemy Declarative)
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment="Agent-specific, domain-specific, or user-specific metadata"
    )
    
    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="memories")
    
    __table_args__ = (
        Index("ix_memories_agent_tier", "agent_id", "tier"),
        Index("ix_memories_agent_type", "agent_id", "memory_type"),
        Index("ix_memories_status_decay", "status", "decay_factor"),
        Index("ix_memories_session", "session_id"),
    )


class SharedMemory(Base):
    """Cross-agent shared knowledge graph (§7B LangMem daemon output).
    
    Extracted patterns from individual agent memories that are
    promoted to shared knowledge for coalition-wide use.
    """
    
    __tablename__ = "shared_memories"
    
    pattern_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique pattern identifier"
    )
    
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        comment="Intent pattern, anti-pattern, coalition-insight, etc."
    )
    
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Compressed pattern description"
    )
    
    source_agent_ids: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
        comment="Agents that contributed to this pattern"
    )
    
    source_memory_ids: Mapped[List[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        server_default="{}",
        comment="Individual memories that were consolidated"
    )
    
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        comment="Aggregate confidence from source agents"
    )
    
    frequency: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="How many times this pattern has been observed"
    )
    
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        ARRAY(Float),
        nullable=True,
        comment="Vector embedding for semantic search"
    )
    
    # Metadata (renamed from 'metadata' because it is reserved in SQLAlchemy Declarative)
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment="Additional pattern metadata"
    )
    
    __table_args__ = (
        Index("ix_shared_category_confidence", "category", "confidence"),
    )


class MemoryDefenseLog(Base):
    """Contamination probe and quarantine events (§16C Context Poisoning Defense).
    
    Tracks memory validation failures, quarantine actions, and recoveries.
    """
    
    __tablename__ = "memory_defense_logs"
    
    memory_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("agent_memories.id"),
        nullable=False,
        index=True
    )
    
    probe_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="contamination, adversarial, drift, hallucination"
    )
    
    severity: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="low, medium, high, critical"
    )
    
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    action_taken: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="quarantined",
        comment="quarantined, released, rejected, baselines_rebuilt"
    )
    
    evidence: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment="Probe results, confidence scores, anomaly metrics"
    )
    
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    resolved_by: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="Agent ID or admin user who resolved"
    )