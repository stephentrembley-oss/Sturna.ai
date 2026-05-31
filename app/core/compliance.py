"""Compliance Classifier — Sturna.ai pre-agent security gate.

Based on Polsia's src/lib/compliance-classifier.js (210 lines)

Features:
•  PII detection: regex patterns + keyword matching (SSN, credit card, email, etc.)
•  MNPI hard rejection: unreleased earnings, M&A, insider trading language
•  Coalition routing based on intent domain
•  Inline classification before agent delegation
"""
import re
from typing import Dict, Any, Optional, List
from enum import Enum as PyEnum

import structlog

logger = structlog.get_logger("compliance_classifier")


class ComplianceCategory(PyEnum):
    """Intent classification categories."""
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    CONTENT = "content"
    RESEARCH = "research"
    LEGAL = "legal"
    MEDICAL = "medical"
    SUPPLY = "supply"
    TRADING = "trading"
    GENERAL = "general"


class ComplianceRisk(PyEnum):
    """Risk levels for compliance classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceClassifier:
    """Inline PII/MNPI classification before agent delegation.
    All intents pass through this gate before entering the IntentEngine.
    """

    # PII regex patterns
    PII_PATTERNS = {
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b"),
        "credit_card": re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        "phone": re.compile(r"\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
        "dob": re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b"),
        "tax_id": re.compile(r"\b\d{2}-\d{7}\b"),  # EIN format
    }

    # MNPI keywords (Material Non-Public Information)
    MNPI_KEYWORDS = [
        "unreleased earnings",
        "earnings before release",
        "merger and acquisition",
        "m&a discussion",
        "acquisition target",
        "takeover",
        "insider trading",
        "material non-public",
        "confidential deal",
        "pending announcement",
        "not yet public",
        "before press release",
        "internal only",
        "board discussion",
        "due diligence",
        "term sheet",
        "loi signed",
    ]

    # Category keywords for routing
    CATEGORY_KEYWORDS = {
        ComplianceCategory.FINANCIAL: [
            "sec filing", "10-k", "10-q", "finra", "ria", "portfolio", "risk assessment",
            "compliance audit", "regulatory", "financial statement", "audit",
        ],
        ComplianceCategory.TECHNICAL: [
            "code review", "security scan", "vulnerability", "dependency", "infrastructure",
            "devops", "ci/cd", "penetration test", "security audit",
        ],
        ComplianceCategory.CONTENT: [
            "content strategy", "seo", "brand voice", "copywriting", "marketing",
            "social media", "blog post", "whitepaper",
        ],
        ComplianceCategory.RESEARCH: [
            "research", "literature review", "study", "hypothesis", "data analysis",
            "synthesis", "survey", "experiment",
        ],
        ComplianceCategory.LEGAL: [
            "legal", "regulatory", "gdpr", "hipaa", "soc 2", "policy", "contract",
            "terms of service", "privacy policy", "compliance framework",
        ],
        ComplianceCategory.MEDICAL: [
            "clinical trial", "fda", "hipaa", "medical device", "patient data",
            "healthcare", "pharma", "adverse event", "drug safety",
        ],
        ComplianceCategory.SUPPLY: [
            "supply chain", "vendor", "esg", "logistics", "procurement",
            "resilience", "supplier risk", "sustainability",
        ],
        ComplianceCategory.TRADING: [
            "trading", "quant", "alpha", "backtest", "market microstructure",
            "algorithmic trading", "high frequency", "portfolio optimization",
        ],
    }

    def __init__(self):
        self.blocked_patterns = 0
        self.total_classified = 0

    async def classify(
        self,
        intent_text: str,
        pre_category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Classify intent for compliance, PII, MNPI, and routing.
        
        Returns:
            {
                "blocked": bool,
                "reason": str (if blocked),
                "category": str,
                "coalition": str,
                "risk_level": str,
                "pii_detected": List[str],
                "mnpi_detected": bool,
            }
        """
        self.total_classified += 1
        text_lower = intent_text.lower()
        
        # 1. PII Detection
        pii_found = self._detect_pii(intent_text)
        
        # 2. MNPI Detection
        mnpi_found = self._detect_mnpi(text_lower)
        
        # 3. Hard Rejection Rules
        if mnpi_found:
            self.blocked_patterns += 1
            logger.warning(
                "mnpi_blocked",
                text_preview=intent_text[:100],
                mnpi_detected=True,
            )
            return {
                "blocked": True,
                "reason": "MNPI detected: Material Non-Public Information cannot be processed",
                "category": "blocked",
                "coalition": "none",
                "risk_level": ComplianceRisk.CRITICAL.value,
                "pii_detected": pii_found,
                "mnpi_detected": True,
            }
        
        # 4. Category Classification
        if pre_category:
            category = self._normalize_category(pre_category)
        else:
            category = self._classify_category(text_lower)
        
        coalition = self._category_to_coalition(category)
        
        # 5. Risk Assessment
        risk_level = self._assess_risk(pii_found, mnpi_found, category)
        
        result = {
            "blocked": False,
            "reason": None,
            "category": category.value,
            "coalition": coalition,
            "risk_level": risk_level.value,
            "pii_detected": pii_found,
            "mnpi_detected": mnpi_found,
        }
        
        logger.info(
            "intent_classified",
            category=category.value,
            coalition=coalition,
            risk=risk_level.value,
            pii_count=len(pii_found),
        )
        
        return result

    def _detect_pii(self, text: str) -> List[str]:
        """Detect PII patterns in text."""
        found = []
        for pii_type, pattern in self.PII_PATTERNS.items():
            if pattern.search(text):
                found.append(pii_type)
        return found

    def _detect_mnpi(self, text_lower: str) -> bool:
        """Detect MNPI keywords in text."""
        return any(keyword in text_lower for keyword in self.MNPI_KEYWORDS)

    def _classify_category(self, text_lower: str) -> ComplianceCategory:
        """Classify intent into category based on keyword matching."""
        scores = {}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = score
        
        best_category = max(scores, key=scores.get)
        
        if scores[best_category] == 0:
            return ComplianceCategory.GENERAL
        
        return best_category

    def _normalize_category(self, category_str: str) -> ComplianceCategory:
        """Normalize string category to enum."""
        mapping = {
            "financial": ComplianceCategory.FINANCIAL,
            "technical": ComplianceCategory.TECHNICAL,
            "content": ComplianceCategory.CONTENT,
            "research": ComplianceCategory.RESEARCH,
            "legal": ComplianceCategory.LEGAL,
            "medical": ComplianceCategory.MEDICAL,
            "supply": ComplianceCategory.SUPPLY,
            "trading": ComplianceCategory.TRADING,
        }
        return mapping.get(category_str.lower(), ComplianceCategory.GENERAL)

    def _category_to_coalition(self, category: ComplianceCategory) -> str:
        """Map compliance category to agent coalition."""
        mapping = {
            ComplianceCategory.FINANCIAL: "financial-analysis",
            ComplianceCategory.TECHNICAL: "technical-audit",
            ComplianceCategory.CONTENT: "content-strategy",
            ComplianceCategory.RESEARCH: "research-synthesis",
            ComplianceCategory.LEGAL: "legal-compliance",
            ComplianceCategory.MEDICAL: "medical-review",
            ComplianceCategory.SUPPLY: "supply-chain",
            ComplianceCategory.TRADING: "trading-quant",
            ComplianceCategory.GENERAL: "research-synthesis",
        }
        return mapping.get(category, "research-synthesis")

    def _assess_risk(
        self,
        pii_found: List[str],
        mnpi_found: bool,
        category: ComplianceCategory,
    ) -> ComplianceRisk:
        """Assess overall risk level."""
        if mnpi_found:
            return ComplianceRisk.CRITICAL
        if len(pii_found) > 2:
            return ComplianceRisk.HIGH
        if len(pii_found) > 0:
            return ComplianceRisk.MEDIUM
        if category in [ComplianceCategory.LEGAL, ComplianceCategory.MEDICAL]:
            return ComplianceRisk.MEDIUM
        return ComplianceRisk.LOW

    def get_stats(self) -> Dict[str, Any]:
        """Get classification statistics."""
        return {
            "total_classified": self.total_classified,
            "blocked_patterns": self.blocked_patterns,
            "block_rate": self.blocked_patterns / max(self.total_classified, 1),
        }


# Singleton factory
_classifier = None

def get_compliance_classifier() -> ComplianceClassifier:
    """Get or create ComplianceClassifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = ComplianceClassifier()
    return _classifier