"""Demo API — Demo session tracking and nurture triggers."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.demo import DemoSession, DemoStatus, Visitor, NurtureStage

router = APIRouter()


@router.post("")
async def start_demo(
    visitor_id: str,
    session_type: str = "agent_auction",
    db: AsyncSession = Depends(get_db),
):
    """Start a new demo session."""
    demo = DemoSession(
        visitor_id=visitor_id,
        session_type=session_type,
        status=DemoStatus.STARTED.value,
    )
    db.add(demo)
    await db.commit()
    await db.refresh(demo)

    return {"demo_id": str(demo.id), "visitor_id": visitor_id, "status": "started"}


@router.post("/{demo_id}/complete")
async def complete_demo(
    demo_id: str,
    intent_submitted: str,
    result_delivered: str,
    agent_shown: str,
    execution_time_ms: float,
    cta_clicked: bool = False,
    cta_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Complete a demo session and trigger nurture sequence."""
    result = await db.execute(
        update(DemoSession)
        .where(DemoSession.id == demo_id)
        .values(
            status=DemoStatus.COMPLETED.value,
            intent_submitted=intent_submitted,
            result_delivered=result_delivered,
            agent_shown=agent_shown,
            execution_time_ms=execution_time_ms,
            cta_clicked=cta_clicked,
            cta_type=cta_type,
        )
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Demo session not found")

    demo_result = await db.execute(select(DemoSession).where(DemoSession.id == demo_id))
    demo = demo_result.scalar_one()

    await db.execute(
        update(Visitor)
        .where(Visitor.id == demo.visitor_id)
        .values(
            demo_completed=True,
            demo_completed_at=func.now(),
            nurture_stage=NurtureStage.EMAIL_1_SENT.value,
            email1_sent_at=func.now(),
        )
    )

    await db.commit()

    return {
        "demo_id": demo_id,
        "status": "completed",
        "nurture_triggered": True,
        "next_email": "email_2_in_48h",
    }


@router.get("/{demo_id}")
async def get_demo(demo_id: str, db: AsyncSession = Depends(get_db)):
    """Get demo session details."""
    result = await db.execute(select(DemoSession).where(DemoSession.id == demo_id))
    demo = result.scalar_one_or_none()
    if not demo:
        raise HTTPException(status_code=404, detail="Demo session not found")

    return demo.to_dict()