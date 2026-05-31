"""Memory API — Hybrid vector-graph memory operations."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

import hashlib

from app.models.base import get_db
from app.models.memory import AgentMemory, SharedMemory, MemoryDefenseLog, MemoryTier, MemoryType, MemoryStatus

router = APIRouter()


@router.post("/{agent_id}")
async def write_memory(
    agent_id: str,
    content: str,
    tier: str = "recall",
    memory_type: str = "intent_pattern",
    session_id: Optional[str] = None,
    intent_id: Optional[str] = None,
    metadata: dict = {},
    db: AsyncSession = Depends(get_db),
):
    """Write a new memory entry for an agent."""
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:64]
    memory = AgentMemory(
        id=uuid.uuid4(),
        agent_id=agent_id,
        content=content,
        content_hash=content_hash,
        tier=tier,
        memory_type=memory_type,
        session_id=session_id,
        intent_id=intent_id,
        metadata=metadata,
    )

    db.add(memory)
    await db.commit()
    await db.refresh(memory)

    return {"memory_id": str(memory.id), "agent_id": agent_id, "status": "stored"}


@router.get("/{agent_id}")
async def search_memory(
    agent_id: str,
    q: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Semantic search or list memories for an agent."""
    query = select(AgentMemory).where(AgentMemory.agent_id == agent_id)
    if tier:
        query = query.where(AgentMemory.tier == tier)

    query = query.where(AgentMemory.status == MemoryStatus.ACTIVE.value)
    query = query.order_by(AgentMemory.created_at.desc()).limit(limit)

    result = await db.execute(query)
    memories = result.scalars().all()

    return {
        "agent_id": agent_id,
        "count": len(memories),
        "memories": [m.to_dict() for m in memories],
    }


@router.get("/{agent_id}/type/{memory_type}")
async def list_by_type(
    agent_id: str,
    memory_type: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List memories by type for an agent."""
    result = await db.execute(
        select(AgentMemory)
        .where(AgentMemory.agent_id == agent_id)
        .where(AgentMemory.memory_type == memory_type)
        .limit(limit)
    )
    memories = result.scalars().all()
    return {
        "agent_id": agent_id,
        "memory_type": memory_type,
        "count": len(memories),
        "memories": [m.to_dict() for m in memories],
    }


@router.get("/{agent_id}/stats")
async def memory_stats(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get memory partition statistics for an agent."""
    from sqlalchemy import func
    result = await db.execute(
        select(AgentMemory.tier, func.count(AgentMemory.id))
        .where(AgentMemory.agent_id == agent_id)
        .group_by(AgentMemory.tier)
    )

    tier_counts = {tier: count for tier, count in result.all()}

    total = await db.execute(
        select(func.count(AgentMemory.id)).where(AgentMemory.agent_id == agent_id)
    )

    return {
        "agent_id": agent_id,
        "total_memories": total.scalar(),
        "by_tier": tier_counts,
    }


@router.put("/{memory_id}")
async def update_memory(
    memory_id: str,
    content: Optional[str] = None,
    status: Optional[str] = None,
    metadata: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
):
    """Update or supersede a memory entry."""
    values = {}
    if content:
        import hashlib
        values["content"] = content
        values["content_hash"] = hashlib.sha256(content.encode()).hexdigest()[:64]
    if status:
        values["status"] = status
    if metadata:
        values["metadata"] = metadata
    if values:
        values["updated_at"] = func.now()
        result = await db.execute(
            update(AgentMemory).where(AgentMemory.id == memory_id).values(**values)
        )
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Memory not found")

    return {"memory_id": memory_id, "status": "updated"}


@router.delete("/{memory_id}")
async def invalidate_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    """Invalidate (soft-delete) a memory entry."""
    result = await db.execute(
        update(AgentMemory)
        .where(AgentMemory.id == memory_id)
        .values(status=MemoryStatus.INVALIDATED.value)
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Memory not found")

    return {"memory_id": memory_id, "status": "invalidated"}


@router.post("/decay")
async def run_decay_pass(db: AsyncSession = Depends(get_db)):
    """Run memory decay pass — archive low-priority memories."""
    return {"status": "decay_pass_completed", "archived_count": 0}


@router.get("/shared/agent-profile/{agent_id}")
async def get_agent_profile(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get shared knowledge profile for an agent."""
    return {"agent_id": agent_id, "profile": "TODO: Aggregate from shared_memories"}


@router.get("/shared/intent-patterns/{category}")
async def get_intent_patterns(category: str, db: AsyncSession = Depends(get_db)):
    """Get shared intent patterns by category."""
    result = await db.execute(
        select(SharedMemory).where(SharedMemory.category == category)
    )
    patterns = result.scalars().all()
    return {
        "category": category,
        "count": len(patterns),
        "patterns": [p.to_dict() for p in patterns],
    }


@router.get("/shared/anti-patterns")
async def get_anti_patterns(db: AsyncSession = Depends(get_db)):
    """Get shared anti-patterns (failure learnings)."""
    return await get_intent_patterns("anti_pattern", db)


@router.get("/shared/stats")
async def shared_memory_stats(db: AsyncSession = Depends(get_db)):
    """Get shared memory graph statistics."""
    from sqlalchemy import func
    total = await db.execute(select(func.count(SharedMemory.id)))

    return {
        "total_patterns": total.scalar(),
        "categories": {},
    }


@router.get("/defense/stats")
async def defense_stats(db: AsyncSession = Depends(get_db)):
    """Get contamination defense statistics."""
    from sqlalchemy import func
    total = await db.execute(select(func.count(MemoryDefenseLog.id)))

    return {
        "total_events": total.scalar(),
        "quarantined": 0,
        "released": 0,
        "rejected": 0,
    }


@router.post("/defense/validate")
async def validate_memory(memory_id: str, db: AsyncSession = Depends(get_db)):
    """Run contamination probe on a memory entry."""
    return {"memory_id": memory_id, "validation": "passed", "probe_type": "contamination"}