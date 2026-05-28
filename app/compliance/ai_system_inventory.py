from typing import Dict, List, Any
from enum import Enum


class RiskLevel(str, Enum):
    MINIMAL = "minimal"
    LIMITED = "limited"
    HIGH = "high"
    PROHIBITED = "prohibited"


class AISystemInventory:
    """
    NIST AI RMF + EU AI Act aligned AI System Inventory.
    Maintains registry of all AI systems with risk classification.
    """

    def __init__(self):
        self.systems: Dict[str, Dict[str, Any]] = {}

    def register_system(
        self,
        system_id: str,
        name: str,
        description: str,
        risk_level: RiskLevel,
        owner: str,
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        entry = {
            "system_id": system_id,
            "name": name,
            "description": description,
            "risk_level": risk_level.value,
            "owner": owner,
            "metadata": metadata or {},
            "eu_ai_act_high_risk": risk_level == RiskLevel.HIGH,
        }
        self.systems[system_id] = entry
        return entry

    def get_system(self, system_id: str) -> Dict[str, Any] | None:
        return self.systems.get(system_id)

    def list_systems(self, risk_level: RiskLevel | None = None) -> List[Dict[str, Any]]:
        if risk_level:
            return [s for s in self.systems.values() if s["risk_level"] == risk_level.value]
        return list(self.systems.values())

    def generate_nist_report(self) -> Dict[str, Any]:
        return {
            "total_systems": len(self.systems),
            "by_risk": {
                level.value: len([s for s in self.systems.values() if s["risk_level"] == level.value])
                for level in RiskLevel
            },
            "high_risk_systems": [s for s in self.systems.values() if s["eu_ai_act_high_risk"]],
        }
