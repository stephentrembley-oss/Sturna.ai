"""Agent API — CRUD + registry + health + quarantine."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.agent import Agent, AgentIdentityRegistry, AgentStatus, AgentTier, AgentClass

router = APIRouter()


@router.get("", response_model=List[dict])
async def list_agents(
    coalition: Optional[str] = None,
    agent_class: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all agents with optional filtering."""
    query = select(Agent)
    if coalition:
        query = query.where(Agent.coalition == coalition)
    if agent_class:
        query = query.where(Agent.agent_class == agent_class)
    if status:
        query = query.where(Agent.status == status)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    agents = result.scalars().all()

    return [agent.to_dict() for agent in agents]


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get single agent by agent_id."""
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.to_dict()


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: dict, db: AsyncSession = Depends(get_db)):
    """Register a new specialist agent."""
    agent = Agent(
        id=uuid.uuid4(),
        agent_id=agent_data["agent_id"],
        name=agent_data["name"],
        description=agent_data.get("description"),
        agent_class=agent_data["agent_class"],
        coalition=agent_data.get("coalition"),
        capability_hash=agent_data["capability_hash"],
        capabilities=agent_data.get("capabilities", []),
        swarm_score=agent_data.get("swarm_score", 0),
        tier=agent_data.get("tier", "bronze"),
        status=agent_data.get("status", "active"),
        model_endpoint=agent_data.get("model_endpoint"),
        model_name=agent_data.get("model_name"),
        config=agent_data.get("config", {}),
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)

    return agent.to_dict()


@router.post("/{agent_id}/quarantine")
async def quarantine_agent(agent_id: str, reason: str, db: AsyncSession = Depends(get_db)):
    """Quarantine an agent (IML drift detected)."""
    result = await db.execute(
        update(Agent)
        .where(Agent.agent_id == agent_id)
        .values(
            status=AgentStatus.QUARANTINED.value,
            quarantined_at=func.now(),
            quarantine_reason=reason,
            health_score=0.0,
        )
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {"agent_id": agent_id, "status": "quarantined", "reason": reason}


@router.post("/{agent_id}/reinstate")
async def reinstate_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Reinstate a quarantined agent after verification."""
    result = await db.execute(
        update(Agent)
        .where(Agent.agent_id == agent_id)
        .values(
            status=AgentStatus.ACTIVE.value,
            quarantined_at=None,
            quarantine_reason=None,
            health_score=1.0,
        )
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {"agent_id": agent_id, "status": "reinstated"}


@router.get("/{agent_id}/health")
async def get_agent_health(agent_id: str, db: AsyncSession = Depends(get_db)):
    """Get agent health metrics (drift status)."""
    result = await db.execute(select(Agent).where(Agent.agent_id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "agent_id": agent.agent_id,
        "status": agent.status,
        "health_score": agent.health_score,
        "march_score": agent.march_score,
        "success_rate": agent.success_rate,
        "avg_latency_ms": agent.avg_latency_ms,
        "last_active_at": agent.last_active_at.isoformat() if agent.last_active_at else None,
        "quarantined_at": agent.quarantined_at.isoformat() if agent.quarantined_at else None,
        "quarantine_reason": agent.quarantine_reason,
    }