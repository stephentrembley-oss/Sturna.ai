# Sturna.ai Integrated Roadmap

**Version:** 1.0  
**Date:** May 28, 2026  
**Status:** Living Document

This roadmap integrates:
- Implementation work completed on May 28, 2026
- Insights from Sturna.ai strategy documents (7-layer architecture, simulated routing, compliance-as-infrastructure)
- Compliance research synthesis (human oversight, evidence, explainability)

---

## 1. Executive Summary

Sturna.ai is evolving from a multi-agent orchestration platform into a **regulatory-native, compliance-first AI execution infrastructure**. 

On May 28, 2026 we successfully deployed core compliance infrastructure to production (Render) and established a strong foundation in human oversight, evidence generation, and AI system inventory. This roadmap aligns that foundation with the strategic vision of a 7-layer architecture focused on explainability, simulated routing intelligence, and continuous assurance.

**Immediate Strategic Priorities:**
- Support the June 3, 2026 RIA pilot (Reg S-P)
- Build toward EU AI Act readiness (August 2026)
- Establish Sturna.ai as the trusted compliance command center for regulated industries

---

## 2. Current State (May 28, 2026)

### Delivered & Live in Production

| Module | Status | Key Features | Strategic Alignment |
|--------|--------|--------------|---------------------|
| **Human Review Logger** | ✅ Live | Hash-chained decisions, pending review queue, chain integrity verification | Layer 3 (Safety & Compliance), EU AI Act Art. 14, Reg S-P human oversight |
| **Evidence Package Generator** | ✅ Live | Pulls real HumanReviewLog + AISystem data, decision summaries, extra context | Layer 3, SOC 2 evidence, audit readiness |
| **AI System Inventory** | ✅ Live | Database-backed, risk classification, NIST-style reporting | Layer 1 (Agent Registry) + compliance tracking |
| **Deployment & Infrastructure** | ✅ Live | Auto table creation, database layer, GitHub Actions test suite | Production reliability |
| **Observability (Tracing)** | ✅ Foundation | OpenTelemetry instrumentation | Reliability & monitoring |

### Key Wins
- All critical import and syntax issues resolved
- App is live and stable on Render
- Strong foundation in tamper-evident logging and evidence generation
- Automated testing pipeline in place

---

## 3. Strategic Alignment

### Mapping to 7-Layer Vision

| Layer | Description (from Strategy Docs) | Current Coverage | Gap / Opportunity |
|-------|----------------------------------|------------------|-------------------|
| **Layer 1** | Agent Discovery & Registry | Partial (AI System Inventory) | Expand to full agent/model registry with shadow AI detection |
| **Layer 2** | Intelligent Routing Engine | Basic orchestrator | Needs adaptive, learning-based routing (Simulated Routing Intelligence) |
| **Layer 3** | Safety & Compliance Stack | **Strong** | Human Review + Evidence + Inventory. Next: "Show Your Work" explainability |
| **Layer 4** | Divergent Checkers (B2) | Early | Multi-model validation for high-risk decisions |
| **Layer 5** | Thermodynamic Integrity | Not started | System health / entropy monitoring |
| **Layer 6** | Post-Quantum Security | Not started | Future priority |
| **Layer 7** | Decentralized Intelligence Bridge | Not started | Future priority |

### Alignment with Research Insights

- **Human-in-the-loop design** → Strongly addressed via Human Review Logger
- **Explainability as a mandate** → Partially addressed; needs visible "Show Your Work" surfaces
- **Unified evidence fabric** → Good foundation with Evidence Packages
- **Continuous assurance** → Evidence generation is manual; move toward Continuous Control Monitoring

---

## 4. Prioritized Roadmap

### Phase 0 – Foundation (Completed May 28)
- Human Review Logger with cryptographic chain integrity
- Evidence Package generation
- AI System Inventory (DB-backed)
- Deployment stabilization + automated testing

### Phase 1 – Compliance Surface & Explainability (June 2026)
**Goal:** Make compliance visible, defensible, and audit-ready for the RIA pilot.

| Priority | Feature | Description | Target Date |
|----------|---------|-------------|-------------|
| P0 | "Show Your Work" Explainability | Visible rationale, data points, and confidence scores on decisions and risk classifications | June 10 |
| P0 | Enhanced Evidence Export | Regulator-friendly formatting, better provenance, one-click regulatory packs | June 12 |
| P1 | Divergent Checker (B2) Foundation | Lightweight cross-model validation for high-risk tasks | June 20 |
| P1 | Continuous Control Monitoring Hooks | Basic agents that push control status into Sturna.ai | June 25 |

### Phase 2 – Intelligence Layer (July – August 2026)
**Goal:** Move from reactive compliance to intelligent, adaptive orchestration.

| Priority | Feature | Description | Target Date |
|----------|---------|-------------|-------------|
| P1 | Simulated Routing Intelligence | Learning-based agent-task matching using historical performance | July 15 |
| P2 | Thermodynamic Integrity Layer | System health monitoring using control entropy concepts | July 30 |
| P2 | Regulatory Change Impact Analyzer | Auto-tag affected controls/policies when regulations update | August 10 |

### Phase 3 – Advanced Capabilities (Q3–Q4 2026)
- Regulatory Knowledge Graph elements
- Regulatory Simulation / Sandbox capabilities
- Stronger Post-Quantum and decentralized features
- Peer benchmarking and industry advocacy features

---

## 5. Key Gaps & Strategic Opportunities

| Gap | Impact | Recommended Action |
|-----|--------|--------------------|
| Limited visible explainability | High (regulator & buyer trust) | Build "Show Your Work" surfaces in Phase 1 |
| Manual evidence generation | Medium-High | Move toward Continuous Control Monitoring |
| No adaptive routing yet | High (cost & performance) | Prioritize Simulated Routing Intelligence in Phase 2 |
| Marketing & positioning assets | Medium | Use strategy documents + NotebookLM to generate investor & sales materials |

---

## 6. Immediate Next Actions (Recommended)

1. **Build "Show Your Work" Explainability Layer** (Highest leverage right now)
2. Improve Evidence Package formatting and provenance
3. Add basic Continuous Control Monitoring hooks
4. Create investor / sales one-pager using the strategy documents

---

## 7. Success Metrics

- RIA pilot success (June 3, 2026)
- Time-to-generate audit-ready evidence package
- % of high-risk decisions with visible explainability
- Reduction in manual compliance effort (measured via user feedback)

---

*This is a living document. Update after each major milestone.*
