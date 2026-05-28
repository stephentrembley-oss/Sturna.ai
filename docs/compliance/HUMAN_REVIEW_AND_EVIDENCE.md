# Human Review Logging & Evidence Generation

This document explains how to use the new compliance modules added to Sturna.ai.

## Overview

Two core modules were added to support Reg S-P and EU AI Act requirements:

1. **Human Review Logger** — Tamper-evident, hash-chained logging of human oversight decisions.
2. **Evidence Package Generator** — Produces audit-ready packages (SOC 2, EU AI Act, etc.).

## Human Review Logger

### When to use

Call it whenever an important AI decision is made that may require human oversight, especially:
- Auction settlement
- High-risk agent actions
- Escalations

### Integration Example (in orchestrator)

```python
from app.compliance.human_review_service import HumanReviewService

# Inside ShivaLimbOrchestrator
self.review_service = HumanReviewService(self.db_session)

review_log = self.review_service.log_decision(
    task_id=task_id,
    agent_id=winning_agent_id,
    decision="approve",           # or escalate
    reviewer_id="compliance-officer-42",
    justification="Approved after reviewing risk score",
    metadata={"auction_id": auction_id}
)
```

### API Endpoints

- `POST /api/v1/reviews/` — Log a new review decision
- `GET /api/v1/reviews/pending` — Get pending reviews
- `GET /api/v1/reviews/verify/{task_id}` — Verify chain integrity

## Evidence Package Generation

### Usage

```python
from app.compliance.soc2_evidence_service import SOC2EvidenceService

service = SOC2EvidenceService(db)
package = service.generate_package(
    framework="soc2",
    period_start=...,
    period_end=...,
    generated_by="compliance-bot"
)
```

The service now automatically pulls real `HumanReviewLog` records for the given period.

### API Endpoints

- `POST /api/v1/evidence/generate` — Generate a new evidence package
- `GET /api/v1/evidence/{package_id}` — Retrieve a previously generated package

## AI System Inventory

Also added for NIST AI RMF + EU AI Act alignment:

- `POST /api/v1/ai-inventory/register`
- `GET /api/v1/ai-inventory/`
- `GET /api/v1/ai-inventory/nist-report`

## Next Steps / Recommendations

- Wire more decision points in the orchestrator to call `HumanReviewService`
- Add actual prompt logging so Evidence packages become richer
- Schedule daily/weekly evidence package generation
- Add tests for the new compliance services
