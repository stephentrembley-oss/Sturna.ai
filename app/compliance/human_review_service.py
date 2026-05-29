import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.human_review import HumanReviewLog


class HumanReviewService:
    def __init__(self, db: Session):
        self.db = db

    def _chain_hash(self, prev_hash: str, data: dict) -> str:
        payload = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(f"{prev_hash}|{payload}".encode()).hexdigest()

    def log_decision(
        self,
        task_id: str,
        agent_id: str,
        decision: str,
        reviewer_id: str,
        justification: Optional[str] = None,
        reviewer_role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        triggered_rules: Optional[List[str]] = None,
        regulations: Optional[List[str]] = None,
        previous_decision_id: Optional[str] = None,
    ) -> HumanReviewLog:

        # Merge triggered_rules and regulations into metadata for explainability
        final_metadata = metadata or {}
        if triggered_rules:
            final_metadata["triggered_rules"] = triggered_rules
        if regulations:
            final_metadata["regulations"] = regulations

        decision_id = hashlib.sha256(
            f"{task_id}:{agent_id}:{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:32]

        previous_hash = "GENESIS"
        if previous_decision_id:
            prev = self.db.query(HumanReviewLog).filter_by(decision_id=previous_decision_id).first()
            if prev:
                previous_hash = prev.chain_hash

        current_data = {
            "decision_id": decision_id,
            "task_id": task_id,
            "agent_id": agent_id,
            "decision": decision,
            "justification": justification,
            "reviewer_id": reviewer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        chain_hash = self._chain_hash(previous_hash, current_data)

        entry = HumanReviewLog(
            decision_id=decision_id,
            task_id=task_id,
            agent_id=agent_id,
            decision=decision,
            justification=justification,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            previous_decision_id=previous_decision_id,
            chain_hash=chain_hash,
            metadata_json=final_metadata,
            is_pending=(decision == "escalate"),
        )

        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_pending_reviews(self, reviewer_id: Optional[str] = None):
        query = self.db.query(HumanReviewLog).filter_by(is_pending=True)
        if reviewer_id:
            query = query.filter_by(reviewer_id=reviewer_id)
        return query.order_by(HumanReviewLog.created_at.desc()).all()

    def verify_chain(self, task_id: str) -> bool:
        logs = self.db.query(HumanReviewLog).filter_by(task_id=task_id).order_by(HumanReviewLog.created_at.asc()).all()
        if not logs:
            return True

        previous_hash = "GENESIS"
        for log in logs:
            current_data = {
                "decision_id": log.decision_id,
                "task_id": log.task_id,
                "agent_id": log.agent_id,
                "decision": log.decision,
                "justification": log.justification,
                "reviewer_id": log.reviewer_id,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
            }
            if self._chain_hash(previous_hash, current_data) != log.chain_hash:
                return False
            previous_hash = log.chain_hash
        return True
