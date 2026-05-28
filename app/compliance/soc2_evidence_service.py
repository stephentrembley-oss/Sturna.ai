import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from app.models.evidence_package import EvidencePackage


class SOC2EvidenceService:
    """
    Generates tamper-evident SOC 2 (and other framework) evidence packages.
    Pulls from Human Reviews, prompt logs, model registry, etc.
    """

    def __init__(self, db: Session):
        self.db = db

    def generate_package(
        self,
        framework: str,
        period_start: datetime,
        period_end: datetime,
        generated_by: str,
    ) -> EvidencePackage:

        # TODO: Expand this to pull real data from HumanReviewLog, prompt logs, model registry, etc.
        evidence = {
            "period": {
                "start": period_start.isoformat(),
                "end": period_end.isoformat(),
            },
            "human_reviews_count": 0,   # Placeholder - wire to real query
            "prompt_logs_count": 0,
            "model_registry": {},
            "access_decisions": [],
        }

        package_id = hashlib.sha256(
            json.dumps(evidence, sort_keys=True).encode()
        ).hexdigest()[:32]

        integrity_hash = hashlib.sha256(
            json.dumps(evidence, sort_keys=True).encode()
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
