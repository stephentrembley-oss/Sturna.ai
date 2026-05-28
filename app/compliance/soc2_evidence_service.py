import hashlib
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.evidence_package import EvidencePackage
from app.models.human_review import HumanReviewLog
from app.models.ai_system import AISystem


class SOC2EvidenceService:
    """
    Generates tamper-evident compliance evidence packages.
    Aggregates Human Reviews, AI Systems, and decision events.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_package(
        self,
        framework: str,
        period_start: datetime,
        period_end: datetime,
        generated_by: str,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> EvidencePackage:

        reviews = (
            self.db.query(HumanReviewLog)
            .filter(
                HumanReviewLog.created_at >= period_start,
                HumanReviewLog.created_at <= period_end,
            )
            .all()
        )

        ai_systems = self.db.query(AISystem).all()

        # Basic decision event summary from reviews
        decision_summary = {
            "total_decisions": len(reviews),
            "approved": len([r for r in reviews if r.decision == "approve"]),
            "rejected": len([r for r in reviews if r.decision == "reject"]),
            "escalated": len([r for r in reviews if r.decision == "escalate"]),
            "modified": len([r for r in reviews if r.decision == "modify"]),
        }

        evidence: Dict[str, Any] = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
            },
            "human_reviews": [
                {
                    "decision_id": r.decision_id,
                    "task_id": r.task_id,
                    "agent_id": r.agent_id,
                    "decision": r.decision,
                    "reviewer_id": r.reviewer_id,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reviews
            ],
            "human_reviews_count": len(reviews),
            "decision_summary": decision_summary,
            "ai_systems_registered": [
                {
                    "system_id": s.system_id,
                    "name": s.name,
                    "risk_level": s.risk_level,
                    "eu_ai_act_high_risk": s.eu_ai_act_high_risk,
                }
                for s in ai_systems
            ],
            "ai_systems_count": len(ai_systems),
            "prompt_logs_count": 0,
            "model_registry": {},
            "access_decisions": [],
        }

        if extra_context:
            evidence["extra_context"] = extra_context

        package_id = hashlib.sha256(
            json.dumps(evidence, sort_keys=True, default=str).encode()
        ).hexdigest()[:32]

        integrity_hash = hashlib.sha256(
            json.dumps(evidence, sort_keys=True, default=str).encode()
        ).hexdigest()

        pkg = EvidencePackage(
            package_id=package_id,
            framework=framework,
            period_start=period_start,
            period_end=period_end,
            evidence_json=evidence,
            integrity_hash=integrity_hash,
            generated_by=generated_by,
        )

        self.db.add(pkg)
        self.db.commit()
        self.db.refresh(pkg)
        return pkg
