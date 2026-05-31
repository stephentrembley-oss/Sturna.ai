"""Galaxy Manager — Sturna.ai two-layer agent routing.

Based on Polsia's src/lib/galaxy-manager.js (331 lines) + src/lib/galaxy-group-manager.js (909 lines)

Two-Layer Routing:
1.  Layer 1 (Manifest Floor): Filter agents by capability, health, MARCH score
2.  Layer 2 (Bidding Overlay): Sealed-bid auction among eligible agents

Coalitions:
•  financial-analysis
•  technical-audit
•  content-strategy
•  research-synthesis
•  legal-compliance
•  medical-review
•  supply-chain
•  trading-quant
"""
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import structlog

from app.models.agent import Agent, AgentClass, AgentStatus, AgentTier

logger = structlog.get_logger("galaxy_manager")


@dataclass
class CoalitionConfig:
    """Configuration for a specialist coalition."""
    name: str
    agent_classes: List[str]
    min_swarm_score: int = 200
    min_march_score: float = 80.0
    max_latency_ms: float = 500.0
    required_capabilities: List[str] = None


COALITIONS = {
    "financial-analysis": CoalitionConfig(
        name="financial-analysis",
        agent_classes=["financial_analysis", "trading_quant"],
        min_swarm_score=300,
        required_capabilities=["sec-filing-analysis", "risk-modeling", "portfolio-stress"],
    ),
    "technical-audit": CoalitionConfig(
        name="technical-audit",
        agent_classes=["technical_audit"],
        min_swarm_score=250,
        required_capabilities=["code-review", "security-scan", "dependency-audit"],
    ),
    "content-strategy": CoalitionConfig(
        name="content-strategy",
        agent_classes=["content_strategy"],
        min_swarm_score=150,
        required_capabilities=["copywriting", "seo-analysis", "brand-voice"],
    ),
    "research-synthesis": CoalitionConfig(
        name="research-synthesis",
        agent_classes=["research_synthesis"],
        min_swarm_score=200,
        required_capabilities=["literature-review", "data-synthesis", "hypothesis-generation"],
    ),
    "legal-compliance": CoalitionConfig(
        name="legal-compliance",
        agent_classes=["legal_compliance"],
        min_swarm_score=400,
        required_capabilities=["regulatory-mapping", "gap-analysis", "policy-drafting"],
    ),
    "medical-review": CoalitionConfig(
        name="medical-review",
        agent_classes=["medical_review"],
        min_swarm_score=350,
        required_capabilities=["clinical-trial-review", "adverse-event-analysis", "hipaa-gap"],
    ),
    "supply-chain": CoalitionConfig(
        name="supply-chain",
        agent_classes=["supply_chain"],
        min_swarm_score=200,
        required_capabilities=["vendor-risk", "esg-tracking", "resilience-modeling"],
    ),
    "trading-quant": CoalitionConfig(
        name="trading-quant",
        agent_classes=["trading_quant", "financial_analysis"],
        min_swarm_score=500,
        required_capabilities=["alpha-generation", "backtesting", "market-microstructure"],
    ),
}


class GalaxyManager:
    """Manages agent coalitions and two-layer routing."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.coalitions = COALITIONS
        self.db = None

    def set_db(self, db):
        self.db = db

    async def get_eligible_agents(
        self,
        coalition: str,
        category: Optional[str] = None,
        min_march_score: float = 80.0,
        status: str = AgentStatus.ACTIVE.value,
        limit: int = 50,
    ) -> List[Agent]:
        """Layer 1: Manifest Floor — Filter agents by coalition requirements."""
        from sqlalchemy import select, and_
        
        if not self.db:
            raise RuntimeError("Database session not injected")
        
        config = self.coalitions.get(coalition)
        if not config:
            logger.warning("unknown_coalition", coalition=coalition)
            return []
        
        query = select(Agent).where(
            and_(
                Agent.coalition == coalition,
                Agent.status == status,
                Agent.march_score >= min_march_score,
                Agent.health_score >= 0.7,
            )
        )
        
        if config.min_swarm_score:
            query = query.where(Agent.swarm_score >= config.min_swarm_score)
        
        query = query.order_by(Agent.swarm_score.desc()).limit(limit)
        
        result = await self.db.execute(query)
        agents = result.scalars().all()
        
        logger.info(
            "manifest_floor",
            coalition=coalition,
            requested=limit,
            eligible=len(agents),
        )
        
        return list(agents)

    async def calculate_capability_match(
        self,
        agent: Agent,
        intent_text: str,
        intent_category: str,
    ) -> float:
        """Calculate semantic match between agent capabilities and intent."""
        intent_words = set(intent_text.lower().split())
        agent_caps = set(cap.lower() for cap in agent.capabilities)
        
        overlap = len(intent_words & agent_caps)
        total = len(intent_words | agent_caps)
        
        jaccard = overlap / total if total > 0 else 0.0
        class_boost = 0.2 if intent_category in agent.agent_class else 0.0
        score_boost = agent.swarm_score / 5000
        
        return min(1.0, jaccard + class_boost + score_boost)

    async def detect_coalition_boundary(self, intent_text: str, intent_category: str) -> str:
        """Detect which coalition should handle an intent."""
        text_lower = intent_text.lower()
        
        coalition_keywords = {
            "financial-analysis": ["sec", "finra", "ria", "portfolio", "risk", "compliance", "audit"],
            "technical-audit": ["code", "security", "vulnerability", "dependency", "scan"],
            "content-strategy": ["content", "seo", "brand", "copy", "marketing"],
            "research-synthesis": ["research", "study", "literature", "synthesize", "hypothesis"],
            "legal-compliance": ["legal", "regulatory", "gdpr", "hipaa", "soc2", "policy"],
            "medical-review": ["clinical", "fda", "hipaa", "medical", "patient", "trial"],
            "supply-chain": ["supply", "vendor", "esg", "chain", "logistics"],
            "trading-quant": ["trading", "quant", "alpha", "backtest", "market"],
        }
        
        scores = {c: sum(1 for kw in kws if kw in text_lower) for c, kws in coalition_keywords.items()}
        
        category_map = {
            "financial": "financial-analysis",
            "technical": "technical-audit",
            "content": "content-strategy",
            "research": "research-synthesis",
            "legal": "legal-compliance",
            "medical": "medical-review",
            "supply": "supply-chain",
            "trading": "trading-quant",
        }
        
        if intent_category in category_map:
            scores[category_map[intent_category]] += 5
        
        best = max(scores, key=scores.get)
        logger.info("coalition_detection", category=intent_category, detected=best)
        
        return best


_galaxy_manager = None

def get_galaxy_manager() -> GalaxyManager:
    """Get or create GalaxyManager singleton."""
    global _galaxy_manager
    if _galaxy_manager is None:
        _galaxy_manager = GalaxyManager()
    return _galaxy_manager