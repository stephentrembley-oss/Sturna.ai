from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.compliance.explainability_service import ExplainabilityService


router = APIRouter(prefix="/api/v1/explainability", tags=["Explainability"])


@router.get("/task/{task_id}", summary="Get 'Show Your Work' explanation for a task")
def get_task_explanation(task_id: str, db: Session = Depends(get_db)):
    """
    Returns a structured explanation of decisions and rationale for a given task.
    This is the core 'Show Your Work' endpoint.
    """
    service = ExplainabilityService(db)
    explanation = service.get_explanation_for_task(task_id)

    if not explanation.get("has_explanation"):
        raise HTTPException(status_code=404, detail=explanation.get("message", "No explanation found"))

    return explanation
