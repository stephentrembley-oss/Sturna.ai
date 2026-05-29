from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.human_review import HumanReviewLog


class ExplainabilityService:
    """
    Hybrid Explainability Service (A + B).

    Lightweight mode: Generates rich, structured explanations on-the-fly.
    Future robust mode: Can store explanation snapshots.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_explanation_for_task(self, task_id: str) -> Dict[str, Any]:
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
                "metadata": log.metadata_json or {},
            })

        final_decision = logs[-1].decision if logs else None
        has_human_review = any(log.reviewer_id != "system" for log in logs)

        return {
            "task_id": task_id,
            "has_explanation": True,
            "final_decision": final_decision,
            "has_human_review": has_human_review,
            "decision_count": len(logs),
            "decisions": decisions,
            "summary": self._generate_rich_summary(final_decision, has_human_review, len(logs), logs),
            "triggered_rules": self._extract_triggered_rules(logs),
            "confidence_note": self._generate_confidence_note(final_decision, has_human_review),
        }

    def _generate_rich_summary(self, final_decision: str, has_human_review: bool, decision_count: int, logs: List) -> str:
        if not final_decision:
            return "No decision recorded."

        parts = [f"Final decision: {final_decision.upper()}."]

        if has_human_review:
            parts.append(f"Human oversight applied across {decision_count} step(s).")
        else:
            parts.append("Fully automated decision (no human review).")

        last_justification = logs[-1].justification if logs and logs[-1].justification else None
        if last_justification:
            parts.append(f"Key rationale: {last_justification}")

        parts.append("Full immutable audit trail available.")
        return " ".join(parts)

    def _extract_triggered_rules(self, logs: List[HumanReviewLog]) -> List[str]:
        rules = set()
        for log in logs:
            if log.metadata_json and isinstance(log.metadata_json, dict):
                if "triggered_rules" in log.metadata_json:
                    rules.update(log.metadata_json["triggered_rules"])
                if "regulations" in log.metadata_json:
                    rules.update(log.metadata_json["regulations"])
        return list(rules) if rules else ["General compliance review"]

    def _generate_confidence_note(self, final_decision: str, has_human_review: bool) -> str:
        if has_human_review:
            return "High confidence due to human validation."
        if final_decision in ["approve", "reject"]:
            return "Automated decision — recommend human review for high-stakes tasks."
        return "Requires human validation."

    def save_explanation_snapshot(self, task_id: str, explanation_data: Dict[str, Any]) -> bool:
        print(f"[Explainability] Snapshot saved for task {task_id} (placeholder for future model)")
        return True
