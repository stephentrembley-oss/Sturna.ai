from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.human_review import HumanReviewLog


class ExplainabilityService:
    """
    Hybrid Explainability Service.

    - Lightweight mode: Generates explanations on-the-fly from existing review logs.
    - Can be extended to store structured explanation snapshots (future robust mode).
    """

    def __init__(self, db: Session):
        self.db = db

    def get_explanation_for_task(self, task_id: str) -> Dict[str, Any]:
        """
        Generate a 'Show Your Work' explanation for a given task.
        Pulls from HumanReviewLog records and enriches with context.
        """
        logs = (
            self.db.query(HumanReviewLog)
            .filter_by(task_id=task_id)
            .order_by(HumanReviewLog.created_at.asc())
            .all()
        )

        if not logs:
            return {
                "task_id": task_id,
                "has_explanation": False,
                "message": "No review decisions found for this task."
            }

        decisions = []
        for log in logs:
            decisions.append({
                "decision_id": log.decision_id,
                "decision": log.decision,
                "justification": log.justification,
                "reviewer_id": log.reviewer_id,
                "reviewer_role": log.reviewer_role,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "is_pending": log.is_pending,
            })

        # Build a simple summary
        final_decision = logs[-1].decision if logs else None
        has_human_review = any(log.reviewer_id != "system" for log in logs)

        return {
            "task_id": task_id,
            "has_explanation": True,
            "final_decision": final_decision,
            "has_human_review": has_human_review,
            "decision_count": len(logs),
            "decisions": decisions,
            "summary": self._generate_summary(final_decision, has_human_review, len(logs)),
        }

    def _generate_summary(self, final_decision: str, has_human_review: bool, decision_count: int) -> str:
        if not final_decision:
            return "No decision recorded."

        base = f"Final decision: {final_decision.upper()}. "

        if has_human_review:
            base += f"Involved human oversight across {decision_count} review step(s). "
        else:
            base += "Automated decision with no human review. "

        base += "Full audit trail available via decision chain."
        return base

    # Placeholder for future robust mode (storing structured explanation snapshots)
    def save_explanation_snapshot(self, task_id: str, explanation_data: Dict[str, Any]) -> bool:
        """
        Future: Store a structured explanation snapshot for later retrieval.
        Currently a placeholder.
        """
        # TODO: Create ExplainabilitySnapshot model and persist here
        print(f"[Explainability] Snapshot saved for task {task_id} (placeholder)")
        return True
