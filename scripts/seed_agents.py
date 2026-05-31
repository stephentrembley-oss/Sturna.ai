"""Seed script — Populate Sturna.ai with test specialist agents.
Run: python scripts/seed_agents.py
"""
import asyncio
import uuid
import random
from datetime import datetime

from sqlalchemy import select

from app.models.base import async_session
from app.models.agent import Agent, AgentIdentityRegistry, AgentStatus


# Realistic agent configurations across all 8 coalitions
AGENT_SEEDS = [
    # Financial Analysis
    {
        "agent_id": "fin-sec-analyzer-001",
        "name": "SEC Filing Analyzer",
        "description": "Specialist in SEC 10-K, 10-Q, and 8-K filing analysis with FINRA compliance mapping",
        "agent_class": "financial_analysis",
        "coalition": "financial-analysis",
        "capabilities": ["sec-filing-analysis", "risk-modeling", "portfolio-stress", "finra-mapping", "ria-compliance"],
        "swarm_score": 850,
        "tier": "platinum",
        "model_name": "gpt-4o",
        "cost_per_intent": 0.012,
        "avg_latency_ms": 280,
    },
    {
        "agent_id": "fin-risk-modeler-002",
        "name": "Portfolio Risk Modeler",
        "description": "Quantitative risk assessment for RIA portfolios under SEC 206(4)-7",
        "agent_class": "financial_analysis",
        "coalition": "financial-analysis",
        "capabilities": ["risk-modeling", "portfolio-stress", "var-calculation", "scenario-analysis"],
        "swarm_score": 720,
        "tier": "gold",
        "model_name": "claude-3-5-sonnet",
        "cost_per_intent": 0.015,
        "avg_latency_ms": 340,
    },
    # Technical Audit
    {
        "agent_id": "tech-sec-scanner-001",
        "name": "Security Vulnerability Scanner",
        "description": "OWASP Top 10 and CVE-based security scanning with remediation guidance",
        "agent_class": "technical_audit",
        "coalition": "technical-audit",
        "capabilities": ["security-scan", "code-review", "dependency-audit", "penetration-test"],
        "swarm_score": 910,
        "tier": "diamond",
        "model_name": "gpt-4o",
        "cost_per_intent": 0.018,
        "avg_latency_ms": 220,
    },
    {
        "agent_id": "tech-code-reviewer-002",
        "name": "Senior Code Reviewer",
        "description": "Enterprise code review with SOC 2 Type II control mapping",
        "agent_class": "technical_audit",
        "coalition": "technical-audit",
        "capabilities": ["code-review", "dependency-audit", "ci-cd-audit", "infrastructure-review"],
        "swarm_score": 680,
        "tier": "gold",
        "model_name": "claude-3-5-sonnet",
        "cost_per_intent": 0.014,
        "avg_latency_ms": 310,
    },
    # Legal Compliance
    {
        "agent_id": "legal-gdpr-expert-001",
        "name": "GDPR Compliance Architect",
        "description": "Full GDPR Article 30-32 gap analysis with DPIA automation",
        "agent_class": "legal_compliance",
        "coalition": "legal-compliance",
        "capabilities": ["regulatory-mapping", "gap-analysis", "policy-drafting", "dpia-automation"],
        "swarm_score": 940,
        "tier": "diamond",
        "model_name": "gpt-4o",
        "cost_per_intent": 0.022,
        "avg_latency_ms": 190,
    },
    {
        "agent_id": "legal-hipaa-auditor-002",
        "name": "HIPAA Security Auditor",
        "description": "HIPAA Security Rule §164.312 technical safeguard verification",
        "agent_class": "legal_compliance",
        "coalition": "legal-compliance",
        "capabilities": ["gap-analysis", "policy-drafting", "technical-safeguards", "risk-assessment"],
        "swarm_score": 780,
        "tier": "platinum",
        "model_name": "claude-3-5-sonnet",
        "cost_per_intent": 0.016,
        "avg_latency_ms": 260,
    },
    # Medical Review
    {
        "agent_id": "med-clinical-reviewer-001",
        "name": "Clinical Trial Protocol Reviewer",
        "description": "FDA 21 CFR Part 312 protocol compliance with adverse event detection",
        "agent_class": "medical_review",
        "coalition": "medical-review",
        "capabilities": ["clinical-trial-review", "adverse-event-analysis", "fda-compliance", "protocol-mapping"],
        "swarm_score": 820,
        "tier": "platinum",
        "model_name": "gpt-4o",
        "cost_per_intent": 0.019,
        "avg_latency_ms": 240,
    },
    # Trading Quant
    {
        "agent_id": "quant-alpha-gen-001",
        "name": "Alpha Generation Engine",
        "description": "Quantitative alpha signal generation with backtesting and market microstructure analysis",
        "agent_class": "trading_quant",
        "coalition": "trading-quant",
        "capabilities": ["alpha-generation", "backtesting", "market-microstructure", "portfolio-optimization"],
        "swarm_score": 960,
        "tier": "diamond",
        "model_name": "gpt-4o",
        "cost_per_intent": 0.025,
        "avg_latency_ms": 170,
    },
    # Content Strategy
    {
        "agent_id": "content-seo-strategist-001",
        "name": "Enterprise SEO Strategist",
        "description": "Technical SEO audit with compliance-aware content strategy for regulated industries",
        "agent_class": "content_strategy",
        "coalition": "content-strategy",
        "capabilities": ["seo-analysis", "brand-voice", "copywriting", "content-strategy", "regulatory-content"],
        "swarm_score": 640,
        "tier": "silver",
        "model_name": "claude-3-5-sonnet",
        "cost_per_intent": 0.009,
        "avg_latency_ms": 380,
    },
    # Research Synthesis
    {
        "agent_id": "research-lit-synth-001",
        "name": "Literature Synthesis Engine",
        "description": "Multi-source academic literature review with hypothesis generation and conflict detection",
        "agent_class": "research_synthesis",
        "coalition": "research-synthesis",
        "capabilities": ["literature-review", "data-synthesis", "hypothesis-generation", "conflict-detection"],
        "swarm_score": 710,
        "tier": "gold",
        "model_name": "gpt-4o",
        "cost_per_intent": 0.013,
        "avg_latency_ms": 290,
    },
    # Supply Chain
    {
        "agent_id": "supply-esg-tracker-001",
        "name": "ESG Supply Chain Tracker",
        "description": "Vendor ESG scoring with resilience modeling and CSRD compliance mapping",
        "agent_class": "supply_chain",
        "coalition": "supply-chain",
        "capabilities": ["vendor-risk", "esg-tracking", "resilience-modeling", "csrd-mapping"],
        "swarm_score": 590,
        "tier": "silver",
        "model_name": "claude-3-5-sonnet",
        "cost_per_intent": 0.011,
        "avg_latency_ms": 350,
    },
]


async def seed_agents():
    """Create test agents in the database."""
    async with async_session() as session:
        print(f"Creating {len(AGENT_SEEDS)} specialist agents...")
        
        for seed in AGENT_SEEDS:
            # Check if agent already exists
            result = await session.execute(
                select(Agent).where(Agent.agent_id == seed["agent_id"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  ⚠️  {seed['agent_id']} already exists, skipping")
                continue
            
            # Create agent
            agent = Agent(
                id=uuid.uuid4(),
                agent_id=seed["agent_id"],
                name=seed["name"],
                description=seed["description"],
                agent_class=seed["agent_class"],
                coalition=seed["coalition"],
                capability_hash="sha256_placeholder",  # Would be real hash in production
                capabilities=seed["capabilities"],
                swarm_score=seed["swarm_score"],
                tier=seed["tier"],
                status=AgentStatus.ACTIVE.value,
                health_score=1.0,
                march_score=random.uniform(82.0, 98.0),
                bid_confidence=random.uniform(0.7, 0.95),
                success_rate=random.uniform(0.85, 0.97),
                avg_latency_ms=seed["avg_latency_ms"],
                cost_per_intent=seed["cost_per_intent"],
                model_name=seed["model_name"],
                model_endpoint="https://api.openai.com/v1" if "gpt" in seed["model_name"] else "https://api.anthropic.com",
                config={"temperature": 0.2, "max_tokens": 4000},
                last_active_at=datetime.utcnow(),
            )
            
            session.add(agent)
            await session.flush()
            
            # Create identity registry entry
            registry = AgentIdentityRegistry(
                id=uuid.uuid4(),
                agent_id=seed["agent_id"],
                token_id=f"erc8004-{seed['agent_id']}-{uuid.uuid4().hex[:8]}",
                reputation_history=[{
                    "event": "registration",
                    "swarm_score": seed["swarm_score"],
                    "tier": seed["tier"],
                    "timestamp": datetime.utcnow().isoformat(),
                }],
            )
            
            session.add(registry)
            print(f"  ✅ {seed['agent_id']} ({seed['coalition']}) — {seed['tier']} tier, score {seed['swarm_score']}")
        
        await session.commit()
        print(f"\n✅ Seeded {len(AGENT_SEEDS)} agents successfully")
        print("Run the intent pipeline now to see real bidding competition!")


if __name__ == "__main__":
    asyncio.run(seed_agents())