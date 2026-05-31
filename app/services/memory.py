"""Memory Service — Sturna.ai hybrid vector-graph memory operations.

Based on Polsia's:
•  services/agent-memory-service.js (§7D Hybrid Memory)
•  services/memory-daemon-service.js
•  services/hymem-learning-service.js

Core operations:
•  write_memory: Store new memory entry
•  recall_memory: Semantic search + graph traversal
•  search_by_type: Filter by memory type
•  run_decay: Archive low-priority memories
•  consolidate: Promote patterns to shared knowledge
"""
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.memory import AgentMemory, SharedMemory, MemoryDefenseLog, MemoryTier, MemoryType, MemoryStatus
from app.models.agent import Agent

logger = structlog.get_logger("memory_service")


class MemoryService:
    """Hybrid vector-graph memory operations for agents."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def write_memory(
        self,
        agent_id: str,
        content: str,
        tier: str = "recall",
        memory_type: str = "intent_pattern",
        session_id: Optional[str] = None,
        intent_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Write a new memory entry for an agent."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:64]
        
        # Check for duplicates
        existing = await self.db.execute(
            select(AgentMemory).where(
                and_(
                    AgentMemory.agent_id == agent_id,
                    AgentMemory.content_hash == content_hash,
                    AgentMemory.status == MemoryStatus.ACTIVE.value,
                )
            )
        )
        if existing.scalar_one_or_none():
            logger.info("memory_duplicate_detected", agent_id=agent_id, content_hash=content_hash)
            return {"memory_id": None, "status": "duplicate", "agent_id": agent_id}
        
        memory = AgentMemory(
            id=uuid.uuid4(),
            agent_id=agent_id,
            content=content,
            content_hash=content_hash,
            tier=tier,
            memory_type=memory_type,
            session_id=session_id,
            intent_id=intent_id,
            metadata=metadata or {},
        )
        
        self.db.add(memory)
        await self.db.commit()
        await self.db.refresh(memory)
        
        logger.info(
            "memory_written",
            memory_id=str(memory.id),
            agent_id=agent_id,
            tier=tier,
            type=memory_type,
        )
        
        return {
            "memory_id": str(memory.id),
            "agent_id": agent_id,
            "status": "stored",
            "tier": tier,
        }

    async def recall_memory(
        self,
        agent_id: str,
        query: Optional[str] = None,
        tier: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Recall memories for an agent with optional filtering."""
        stmt = select(AgentMemory).where(
            and_(
                AgentMemory.agent_id == agent_id,
                AgentMemory.status == MemoryStatus.ACTIVE.value,
            )
        )
        
        if tier:
            stmt = stmt.where(AgentMemory.tier == tier)
        if memory_type:
            stmt = stmt.where(AgentMemory.memory_type == memory_type)
        
        # Order by: decay_factor desc, access_count desc, created_at desc
        stmt = stmt.order_by(
            AgentMemory.decay_factor.desc(),
            AgentMemory.access_count.desc(),
            AgentMemory.created_at.desc(),
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        memories = result.scalars().all()
        
        # Update access counts
        for memory in memories:
            memory.access_count += 1
            memory.last_accessed_at = datetime.utcnow()
        
        await self.db.commit()
        
        return [m.to_dict() for m in memories]

    async def search_by_type(
        self,
        agent_id: str,
        memory_type: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search memories by type for an agent."""
        result = await self.db.execute(
            select(AgentMemory)
            .where(
                and_(
                    AgentMemory.agent_id == agent_id,
                    AgentMemory.memory_type == memory_type,
                    AgentMemory.status == MemoryStatus.ACTIVE.value,
                )
            )
            .order_by(AgentMemory.created_at.desc())
            .limit(limit)
        )
        memories = result.scalars().all()
        return [m.to_dict() for m in memories]

    async def get_memory_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get memory partition statistics for an agent."""
        result = await self.db.execute(
            select(AgentMemory.tier, func.count(AgentMemory.id))
            .where(AgentMemory.agent_id == agent_id)
            .group_by(AgentMemory.tier)
        )
        tier_counts = {tier: count for tier, count in result.all()}
        
        total = await self.db.execute(
            select(func.count(AgentMemory.id)).where(AgentMemory.agent_id == agent_id)
        )
        
        return {
            "agent_id": agent_id,
            "total_memories": total.scalar(),
            "by_tier": tier_counts,
        }

    async def run_decay(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Run memory decay pass — archive low-priority memories.
        
        Decay rules:
        - EPISODIC: Archive if last_accessed > 7 days ago
        - RECALL: Archive if last_accessed > 30 days ago AND access_count < 3
        - SEMANTIC: Never auto-archive (decay_factor = 1.0)
        - CORE: Never auto-archive
        """
        archived_count = 0
        
        # Episodic decay (7 days)
        cutoff_episodic = datetime.utcnow() - timedelta(days=7)
        result = await self.db.execute(
            update(AgentMemory)
            .where(
                and_(
                    AgentMemory.tier == MemoryTier.EPISODIC.value,
                    AgentMemory.status == MemoryStatus.ACTIVE.value,
                    or_(
                        AgentMemory.last_accessed_at < cutoff_episodic,
                        AgentMemory.last_accessed_at.is_(None),
                    ),
                )
            )
            .values(
                status=MemoryStatus.ARCHIVED.value,
                archived_at=datetime.utcnow(),
            )
        )
        archived_count += result.rowcount
        
        # Recall decay (30 days, low access)
        cutoff_recall = datetime.utcnow() - timedelta(days=30)
        result = await self.db.execute(
            update(AgentMemory)
            .where(
                and_(
                    AgentMemory.tier == MemoryTier.RECALL.value,
                    AgentMemory.status == MemoryStatus.ACTIVE.value,
                    AgentMemory.access_count < 3,
                    or_(
                        AgentMemory.last_accessed_at < cutoff_recall,
                        AgentMemory.last_accessed_at.is_(None),
                    ),
                )
            )
            .values(
                status=MemoryStatus.ARCHIVED.value,
                archived_at=datetime.utcnow(),
            )
        )
        archived_count += result.rowcount
        
        await self.db.commit()
        
        logger.info("decay_pass_complete", archived_count=archived_count)
        
        return {"archived_count": archived_count, "status": "decay_pass_completed"}

    async def consolidate_shared_memory(
        self,
        category: str,
        min_confidence: float = 0.7,
        min_frequency: int = 3,
    ) -> Dict[str, Any]:
        """Consolidate individual memories into shared knowledge patterns.
        
        Finds frequently observed patterns across agents and promotes them
        to the shared_memories table for coalition-wide use.
        """
        # Find patterns that appear in multiple agents
        result = await self.db.execute(
            select(
                AgentMemory.memory_type,
                AgentMemory.content,
                func.count(AgentMemory.id).label("freq"),
                func.array_agg(AgentMemory.agent_id).label("agents"),
            )
            .where(
                and_(
                    AgentMemory.status == MemoryStatus.ACTIVE.value,
                    AgentMemory.memory_type == category,
                )
            )
            .group_by(AgentMemory.memory_type, AgentMemory.content)
            .having(func.count(AgentMemory.id) >= min_frequency)
        )
        
        patterns = result.all()
        consolidated = 0
        
        for mem_type, content, freq, agents in patterns:
            # Check if already in shared memory
            existing = await self.db.execute(
                select(SharedMemory).where(
                    and_(
                        SharedMemory.category == category,
                        SharedMemory.summary == content[:200],
                    )
                )
            )
            if existing.scalar_one_or_none():
                continue
            
            # Create shared pattern
            shared = SharedMemory(
                id=uuid.uuid4(),
                pattern_id=f"pattern-{uuid.uuid4().hex[:8]}",
                category=category,
                summary=content[:500],
                source_agent_ids=list(set(agents)),
                source_memory_ids=[],  # Would link to specific memory IDs
                confidence=min(1.0, freq / 10.0),
                frequency=freq,
            )
            
            self.db.add(shared)
            consolidated += 1
        
        await self.db.commit()
        
        logger.info("consolidation_complete", category=category, patterns_consolidated=consolidated)
        
        return {
            "category": category,
            "patterns_consolidated": consolidated,
            "min_confidence": min_confidence,
            "min_frequency": min_frequency,
        }

    async def quarantine_memory(
        self,
        memory_id: str,
        reason: str,
        probe_type: str = "contamination",
        severity: str = "high",
    ) -> Dict[str, Any]:
        """Quarantine a memory entry due to contamination detection."""
        # Update memory status
        await self.db.execute(
            update(AgentMemory)
            .where(AgentMemory.id == memory_id)
            .values(status=MemoryStatus.QUARANTINED.value)
        )
        
        # Log defense event
        defense_log = MemoryDefenseLog(
            id=uuid.uuid4(),
            memory_id=memory_id,
            probe_type=probe_type,
            severity=severity,
            action_taken="quarantined",
            evidence={"reason": reason, "detected_at": datetime.utcnow().isoformat()},
        )
        
        self.db.add(defense_log)
        await self.db.commit()
        
        logger.warning("memory_quarantined", memory_id=memory_id, reason=reason, probe_type=probe_type)
        
        return {"memory_id": memory_id, "status": "quarantined", "reason": reason}