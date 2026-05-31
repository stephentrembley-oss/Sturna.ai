"""Visitor API — Lead tracking and attribution."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.demo import Visitor, VisitorSource, NurtureStage

router = APIRouter()


@router.post("")
async def track_visitor(
    fingerprint: str,
    source: str = "organic",
    referrer: Optional[str] = None,
    landing_page: Optional[str] = None,
    email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Track a new visitor or update existing."""
    result = await db.execute(select(Visitor).where(Visitor.fingerprint == fingerprint))
    visitor = result.scalar_one_or_none()
    if visitor:
        visitor.page_views += 1
        visitor.last_seen_at = func.now()
        if email and not visitor.email:
            visitor.email = email
        await db.commit()
        return {"visitor_id": str(visitor.id), "status": "updated"}

    visitor = Visitor(
        fingerprint=fingerprint,
        source=source,
        referrer=referrer,
        landing_page=landing_page,
        email=email,
        page_views=1,
        session_count=1,
    )

    db.add(visitor)
    await db.commit()
    await db.refresh(visitor)

    return {"visitor_id": str(visitor.id), "status": "created"}


@router.get("/{visitor_id}")
async def get_visitor(visitor_id: str, db: AsyncSession = Depends(get_db)):
    """Get visitor profile and journey."""
    result = await db.execute(select(Visitor).where(Visitor.id == visitor_id))
    visitor = result.scalar_one_or_none()
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    return visitor.to_dict()


@router.get("")
async def list_visitors(
    source: Optional[str] = None,
    is_qualified: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List visitors with filtering."""
    query = select(Visitor)
    if source:
        query = query.where(Visitor.source == source)
    if is_qualified is not None:
        query = query.where(Visitor.is_qualified == is_qualified)

    query = query.order_by(Visitor.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    visitors = result.scalars().all()

    return {
        "count": len(visitors),
        "visitors": [v.to_dict() for v in visitors],
    }


@router.post("/{visitor_id}/score")
async def score_visitor(visitor_id: str, score: int, db: AsyncSession = Depends(get_db)):
    """Update lead score for a visitor."""
    result = await db.execute(
        update(Visitor)
        .where(Visitor.id == visitor_id)
        .values(lead_score=score, is_qualified=(score >= 70))
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Visitor not found")

    return {"visitor_id": visitor_id, "lead_score": score, "is_qualified": score >= 70}