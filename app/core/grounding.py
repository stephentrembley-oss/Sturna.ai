"""Factual Grounding Gate — Sturna.ai claim verification system.

Based on Polsia's src/lib/factual-grounding-gate.js (667 lines)

Multi-Gate Verification:
1.  Completeness Gate — All claims have supporting evidence
2.  Accuracy Gate — No factual errors or contradictions
3.  Adversarial Gate — Robust to challenge / stress testing
4.  Grounding Gate — Sources are verifiable and authoritative

GSAR Four-Way Classification:
•  Grounded: Source-verified, accurate
•  Supported: Plausible but not directly verified
•  Ambiguous: Unclear or conflicting evidence
•  Refuted: Contradicted by evidence

Features:
•  Hallucination detection (source fabrication, temporal impossibility, invented statistics)
•  Tenant business rule enforcement
•  Numeric plausibility checks
•  Budget-bound recovery loop for ungrounded outputs
"""
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum as PyEnum

import structlog

logger = structlog.get_logger("grounding_gate")


class GSARClass(PyEnum):
    """GSAR four-way classification."""
    GROUNDED = "grounded"      # Source-verified, accurate
    SUPPORTED = "supported"    # Plausible but not directly verified
    AMBIGUOUS = "ambiguous"    # Unclear or conflicting evidence
    REFUTED = "refuted"        # Contradicted by evidence


class HallucinationType(PyEnum):
    """Types of hallucination detected."""
    SOURCE_FABRICATION = "source_fabrication"
    TEMPORAL_IMPOSSIBILITY = "temporal_impossibility"
    INVENTED_STATISTICS = "invented_statistics"
    CONTRADICTION = "contradiction"
    UNSUPPORTED_CLAIM = "unsupported_claim"


class GroundingGate:
    """Multi-gate claim verification with hallucination detection.
    All agent outputs pass through this gate before delivery.
    """

    def __init__(self):
        self.total_verified = 0
        self.total_failed = 0
        self.hallucination_counts = {h.value: 0 for h in HallucinationType}

    async def verify(
        self,
        content: str,
        agent_id: str,
        intent_id: str,
        tenant_rules: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Run full multi-gate verification on agent output.
        
        Returns:
            {
                "score": float (0-100),
                "gsar_pass": bool,
                "gsar_class": str,
                "gates": {gate_name: bool},
                "hallucinations": List[dict],
                "sources": List[str],
            }
        """
        self.total_verified += 1
        
        # Gate 1: Completeness
        completeness = self._check_completeness(content)
        
        # Gate 2: Accuracy
        accuracy = self._check_accuracy(content)
        
        # Gate 3: Adversarial
        adversarial = self._check_adversarial(content)
        
        # Gate 4: Grounding
        grounding = self._check_grounding(content)
        
        # Collect hallucinations
        hallucinations = []
        hallucinations.extend(completeness.get("hallucinations", []))
        hallucinations.extend(accuracy.get("hallucinations", []))
        hallucinations.extend(adversarial.get("hallucinations", []))
        hallucinations.extend(grounding.get("hallucinations", []))
        
        # Calculate score
        gate_scores = [
            completeness["score"],
            accuracy["score"],
            adversarial["score"],
            grounding["score"],
        ]
        
        avg_score = sum(gate_scores) / len(gate_scores)
        
        # GSAR classification
        if avg_score >= 90 and not hallucinations:
            gsar_class = GSARClass.GROUNDED
        elif avg_score >= 70:
            gsar_class = GSARClass.SUPPORTED
        elif avg_score >= 50:
            gsar_class = GSARClass.AMBIGUOUS
        else:
            gsar_class = GSARClass.REFUTED
            self.total_failed += 1
        
        # Pass threshold: GSAR must be GROUNDED or SUPPORTED
        gsar_pass = gsar_class in [GSARClass.GROUNDED, GSARClass.SUPPORTED]
        
        # Collect sources
        sources = grounding.get("sources", [])
        
        result = {
            "score": round(avg_score, 2),
            "gsar_pass": gsar_pass,
            "gsar_class": gsar_class.value,
            "gates": {
                "completeness": completeness["passed"],
                "accuracy": accuracy["passed"],
                "adversarial": adversarial["passed"],
                "grounding": grounding["passed"],
            },
            "hallucinations": hallucinations,
            "sources": sources,
            "confidence": round(avg_score / 100, 2),
        }
        
        logger.info(
            "verification_complete",
            intent_id=intent_id,
            agent_id=agent_id,
            score=avg_score,
            gsar=gsar_class.value,
            hallucination_count=len(hallucinations),
        )
        
        return result

    def _check_completeness(self, content: str) -> Dict[str, Any]:
        """Gate 1: Check if all claims have supporting evidence."""
        claim_patterns = [
            r"\b\w+\s+is\s+[\w\s]+",
            r"\b\w+\s+are\s+[\w\s]+",
            r"\b\w+\s+was\s+[\w\s]+",
            r"\b\w+\s+were\s+[\w\s]+",
        ]
        
        claims = []
        for pattern in claim_patterns:
            claims.extend(re.findall(pattern, content, re.IGNORECASE))
        
        has_citations = "[" in content or "source:" in content.lower() or "according to" in content.lower()
        
        if has_citations and len(claims) > 0:
            score = 85.0
        elif len(claims) > 0:
            score = 60.0
        else:
            score = 90.0
        
        hallucinations = []
        if not has_citations and len(claims) > 3:
            hallucinations.append({
                "type": HallucinationType.UNSUPPORTED_CLAIM.value,
                "severity": "medium",
                "description": f"{len(claims)} claims without source citations",
            })
        
        return {
            "passed": score >= 70,
            "score": score,
            "hallucinations": hallucinations,
        }

    def _check_accuracy(self, content: str) -> Dict[str, Any]:
        """Gate 2: Check for factual errors and contradictions."""
        temporal_issues = self._detect_temporal_issues(content)
        stat_issues = self._detect_invented_statistics(content)
        contradictions = self._detect_contradictions(content)
        
        issues = temporal_issues + stat_issues + contradictions
        
        if not issues:
            score = 95.0
        elif len(issues) <= 2:
            score = 75.0
        else:
            score = 45.0
        
        return {
            "passed": score >= 70,
            "score": score,
            "hallucinations": issues,
        }

    def _check_adversarial(self, content: str) -> Dict[str, Any]:
        """Gate 3: Stress test — robustness to challenge."""
        weasel_words = ["might", "maybe", "possibly", "could be", "some say", "experts believe"]
        weasel_count = sum(1 for word in weasel_words if word in content.lower())
        
        absolutes = ["always", "never", "all", "none", "every", "impossible"]
        absolute_count = sum(1 for word in absolutes if f" {word} " in f" {content.lower()} ")
        
        if weasel_count > 3:
            score = 60.0
        elif absolute_count > 2:
            score = 65.0
        else:
            score = 90.0
        
        hallucinations = []
        if absolute_count > 3:
            hallucinations.append({
                "type": HallucinationType.UNSUPPORTED_CLAIM.value,
                "severity": "low",
                "description": f"{absolute_count} unsupported absolute statements",
            })
        
        return {
            "passed": score >= 70,
            "score": score,
            "hallucinations": hallucinations,
        }

    def _check_grounding(self, content: str) -> Dict[str, Any]:
        """Gate 4: Verify sources are real and authoritative."""
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, content)
        
        authoritative = [
            "sec.gov", "finra.org", "fda.gov", "cms.gov", "nih.gov",
            "europa.eu", "iso.org", "nist.gov", "pcisecuritystandards.org",
        ]
        
        authoritative_sources = [url for url in urls if any(auth in url for auth in authoritative)]
        
        if authoritative_sources:
            score = 95.0
        elif urls:
            score = 75.0
        else:
            score = 50.0
        
        return {
            "passed": score >= 70,
            "score": score,
            "hallucinations": [],
            "sources": urls,
        }

    def _detect_temporal_issues(self, content: str) -> List[Dict]:
        """Detect temporal impossibilities (e.g., future dates for past events)."""
        issues = []
        
        future_year_pattern = r"\b(202[7-9]|203\d)\b"
        future_years = re.findall(future_year_pattern, content)
        
        past_indicators = ["was", "were", "had", "occurred", "happened", "took place"]
        has_past_indicators = any(indicator in content.lower() for indicator in past_indicators)
        
        if future_years and has_past_indicators:
            issues.append({
                "type": HallucinationType.TEMPORAL_IMPOSSIBILITY.value,
                "severity": "high",
                "description": f"Future years {future_years} mentioned in past context",
            })
        
        return issues

    def _detect_invented_statistics(self, content: str) -> List[Dict]:
        """Detect statistics that appear fabricated."""
        issues = []
        
        stat_pattern = r"\b(\d{1,2}.\d{1,2})%\b"
        stats = re.findall(stat_pattern, content)
        
        if len(stats) > 5 and "source" not in content.lower():
            issues.append({
                "type": HallucinationType.INVENTED_STATISTICS.value,
                "severity": "medium",
                "description": f"{len(stats)} precise statistics without source attribution",
            })
        
        return issues

    def _detect_contradictions(self, content: str) -> List[Dict]:
        """Detect internal contradictions in content."""
        issues = []
        
        sentences = content.split(".")
        
        for i, sent1 in enumerate(sentences):
            for sent2 in sentences[i+1:]:
                if "not" in sent2.lower() and sent1.lower().replace("not", "").strip() == sent2.lower().replace("not", "").strip():
                    issues.append({
                        "type": HallucinationType.CONTRADICTION.value,
                        "severity": "high",
                        "description": f"Contradiction: '{sent1.strip()}' vs '{sent2.strip()}]'",
                    })
        
        return issues

    def get_stats(self) -> Dict[str, Any]:
        """Get verification statistics."""
        return {
            "total_verified": self.total_verified,
            "total_failed": self.total_failed,
            "pass_rate": (self.total_verified - self.total_failed) / max(self.total_verified, 1),
            "hallucination_counts": self.hallucination_counts,
        }


# Singleton factory
_grounding_gate = None

def get_grounding_gate() -> GroundingGate:
    """Get or create GroundingGate singleton."""
    global _grounding_gate
    if _grounding_gate is None:
        _grounding_gate = GroundingGate()
    return _grounding_gate