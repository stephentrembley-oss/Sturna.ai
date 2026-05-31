"""Intents API — Primary endpoint for Sturna multi-agent execution.
This is the main entry point for submitting intents to the system.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.core.intent_engine import get_intent_engine

router = APIRouter()


@router.post("/execute")
async def execute_intent(
    intent_text: str,
    intent_category: Optional[str] = None,
    coalition: Optional[str] = None,
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Execute an intent through the full 5-stage pipeline.
    This is the main entry point for the Sturna multi-agent system.

    Args:
        intent_text: The user's query or task description
        intent_category: Optional pre-classified category
        coalition: Optional target coalition (auto-detected if None)
        session_id: Optional session ID for episodic memory

    Returns:
        Full IntentResult with winner, proof, transparency card
    """
    engine = get_intent_engine()

    # Inject db into subsystems
    from app.core.galaxy_manager import get_galaxy_manager
    from app.core.dag_scheduler import get_dag_scheduler

    gm = get_galaxy_manager()
    gm.set_db(db)

    ds = get_dag_scheduler()
    ds.set_db(db)

    result = await engine.execute_intent(
        intent_text=intent_text,
        intent_category=intent_category,
        coalition=coalition,
        session_id=session_id,
        db=db,
    )

    return result.to_dict()


@router.get("/{intent_id}/status")
async def get_intent_status(intent_id: str):
    """Get status of a previously submitted intent."""
    return {"intent_id": intent_id, "status": "unknown", "message": "Status tracking not yet implemented"}


@router.get("/stats")
async def get_intent_stats():
    """Get aggregate intent execution statistics."""
    engine = get_intent_engine()
    return {
        "total_executed": 0,
        "avg_latency_ms": 0,
        "success_rate": 0,
        "top_coalitions": [],
    }