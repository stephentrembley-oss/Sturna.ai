from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.ai_system import AISystem


class AISystemInventory:
    """
    Database-backed AI System Inventory.
    Supports NIST AI RMF and EU AI Act risk classification.
    """

    def __init__(self, db: Session):
        self.db = db

    def register_system(
        self,
        system_id: str,
        name: str,
        description: str,
        risk_level: str,
        owner: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        existing = self.db.query(AISystem).filter_by(system_id=system_id).first()

        if existing:
            existing.name = name
            existing.description = description
            existing.risk_level = risk_level
            existing.owner = owner
            existing.eu_ai_act_high_risk = (risk_level == "high")
            existing.metadata_json = metadata or {}
            self.db.commit()
            self.db.refresh(existing)
            return existing.to_dict()

        new_system = AISystem(
            system_id=system_id,
            name=name,
            description=description,
            risk_level=risk_level,
            owner=owner,
            eu_ai_act_high_risk=(risk_level == "high"),
            metadata_json=metadata or {},
        )
        self.db.add(new_system)
        self.db.commit()
        self.db.refresh(new_system)
        return new_system.to_dict()

    def get_system(self, system_id: str) -> Optional[Dict[str, Any]]:
        system = self.db.query(AISystem).filter_by(system_id=system_id).first()
        return system.to_dict() if system else None

    def list_systems(self, risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.db.query(AISystem)
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
        return [s.to_dict() for s in query.all()]

    def generate_nist_report(self) -> Dict[str, Any]:
        systems = self.db.query(AISystem).all()
        by_risk = {}
        for level in ["minimal", "limited", "high", "prohibited"]:
            by_risk[level] = len([s for s in systems if s.risk_level == level])

        high_risk = [s.to_dict() for s in systems if s.eu_ai_act_high_risk]

        return {
            "total_systems": len(systems),
            "by_risk": by_risk,
            "high_risk_systems": high_risk,
        }
