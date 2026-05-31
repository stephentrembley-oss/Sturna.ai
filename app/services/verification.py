"""Verification Service — Triple-gate verification runner.

Based on Polsia's services/memory-verification-runner.js (150 intents, 5 domains)
"""
from typing import Dict, Any, List, Optional

import structlog

from app.core.grounding import get_grounding_gate

logger = structlog.get_logger("verification_service")


class VerificationService:
    """Runs the triple-gate verification battery on agent outputs."""

    def __init__(self):
        self.grounding_gate = get_grounding_gate()
        self.total_runs = 0
        self.passed_runs = 0

    async def verify_intent_output(
        self,
        content: str,
        agent_id: str,
        intent_id: str,
    ) -> Dict[str, Any]:
        """Run full verification on an agent's output."""
        self.total_runs += 1
        
        result = await self.grounding_gate.verify(
            content=content,
            agent_id=agent_id,
            intent_id=intent_id,
        )
        
        if result["gsar_pass"]:
            self.passed_runs += 1
        
        logger.info(
            "verification_complete",
            intent_id=intent_id,
            agent_id=agent_id,
            score=result["score"],
            passed=result["gsar_pass"],
        )
        
        return result

    async def batch_verify(
        self,
        outputs: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Verify multiple outputs in batch."""
        results = []
        for output in outputs:
            result = await self.verify_intent_output(
                content=output["content"],
                agent_id=output["agent_id"],
                intent_id=output["intent_id"],
            )
            results.append(result)
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get verification statistics."""
        return {
            "total_runs": self.total_runs,
            "passed_runs": self.passed_runs,
            "pass_rate": self.passed_runs / max(self.total_runs, 1),
        }


# Singleton
_service = None

def get_verification_service() -> VerificationService:
    global _service
    if _service is None:
        _service = VerificationService()
    return _service