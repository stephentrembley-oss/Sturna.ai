from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.compliance.human_review_service import HumanReviewService
from app.schemas.human_review import HumanReviewCreate, HumanReviewOut


router = APIRouter(prefix="/api/v1/reviews", tags=["Human Review & Oversight"])


@router.post("/", response_model=HumanReviewOut, summary="Log a human review decision")
def create_human_review(
    payload: HumanReviewCreate,
    db: Session = Depends(get_db),
):
    """
    Log a human oversight decision with tamper-evident hash chaining.
    Critical for Reg S-P and EU AI Act Article 14 compliance.
    """
    service = HumanReviewService(db)
    return service.log_decision(
        task_id=payload.task_id,
        agent_id=payload.agent_id,
        decision=payload.decision.value,
        reviewer_id=payload.reviewer_id,
        justification=payload.justification,
        reviewer_role=payload.reviewer_role,
        metadata=payload.metadata,
        previous_decision_id=payload.previous_decision_id,
    )


@router.get("/pending", response_model=List[HumanReviewOut], summary="Get pending reviews for a reviewer")
def get_pending_reviews(
    reviewer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    service = HumanReviewService(db)
    return service.get_pending_reviews(reviewer_id)


@router.get("/verify/{task_id}", summary="Verify chain integrity for a task")
def verify_review_chain(task_id: str, db: Session = Depends(get_db)):
    service = HumanReviewService(db)
    is_valid = service.verify_chain_integrity(task_id)
    return {"task_id": task_id, "chain_valid": is_valid}
