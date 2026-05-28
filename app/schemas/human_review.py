from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReviewDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    ESCALATE = "escalate"


class HumanReviewCreate(BaseModel):
    task_id: str
    agent_id: str
    decision: ReviewDecision
    justification: Optional[str] = None
    reviewer_id: str
    reviewer_role: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    previous_decision_id: Optional[str] = None


class HumanReviewOut(BaseModel):
    decision_id: str
    task_id: str
    agent_id: str
    decision: str
    justification: Optional[str]
    reviewer_id: str
    reviewer_role: Optional[str]
    created_at: datetime
    is_pending: bool

    class Config:
        from_attributes = True
