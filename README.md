# Sturna.ai

**Compliance Intelligence, Verified by Design**

Sturna is the self-healing autonomous multi-agent orchestration platform purpose-built for regulated industries. 446+ specialist agents compete in real-time sealed-bid Coalition Market Auctions. The highest-confidence agent executes every task — with cryptographic zk-SNARK proof, WORM audit trails, MARCH verification, and full regulatory-grade evidence.

No routing code. No static DAGs. Just verifiable intelligence that compliance officers, CCOs, and risk managers can trust and defend in audits.

> "Audit-ready in minutes, not months. Gap analysis before the deadline."

## Mission
Eliminate compliance blind spots for finance (RIAs), healthcare, legal, and SaaS by deploying competitive multi-agent intelligence that verifies every claim, grounds every finding in evidence, and delivers audit-ready results faster and more reliably than any single-model system.

**Positioning**: The AI execution layer built for compliant industries. Not an AI tool — an AI marketplace where the best specialized intelligence always wins, and every win is provably correct.

## What's Built (Production)

- **446+ Competing Specialist Agents** across Trading/Quant, Legal, Supply Chain, Compliance, Medical verticals
- **Coalition Market Auction** with 86%+ first-attempt success rate and self-healing failover
- **Full Biomimetic Foundation** — ShivaLimbOrchestrator, Octopus Neural architecture, CRISPR-AgentEditor, cephalopod-inspired RNA editing for meta-adaptation
- **20-Stage Execution Pipeline** + all core safety gates (GSAR, MARCH, CMAG, IML, Platt Scaling, etc.)
- **zk-SNARK Cryptographic Moat 2.0** — Poseidon-optimized Circom circuits, Nova-Scotia recursive folding (constant-size verifier), Groth16 final proof on zkSync Era Sepolia (live)
- **End-to-end latency <18ms** proven live
- **Compliance Pages Live** — EU AI Act, HIPAA, SOC 2 Type II (Day 134/180), Reg S-P
- **Live Product Assets** — Agent auction demo, live bidding viz, vertical scanners, PDF report generation, pilot workspace
- **Monetization** — Free Scanner → Pro ($29/mo or $290/yr) → Pilot ($2,500) → Enterprise
- **Automated 3-Email Nurture** triggered on demo completion

## Brand Voice & Positioning

Sturna speaks to compliance officers, GCOs, GRC leads, and risk managers — not CTOs or crypto communities.

- Lead with the penalty, not the tech (SEC fines, OCR enforcement, deal stalls, Reg S-P June 3 deadline)
- Evidence-first: Every claim backed by signed, verifiable proof. Never ask buyers to "trust us."
- Authoritative on regulation: SEC, HIPAA, SOC 2, EU AI Act
- Urgency without panic
- Specific data beats generic claims

**Absolute rules**: No fight metaphors. Expand every acronym on first use. Never discuss internal routing architecture, Bittensor, or agent counts in customer-facing copy.

Tagline: **"Compliance Intelligence, Verified by Design"**

## Tech Stack

- Backend: Node.js / Express + Neon PostgreSQL (company-scoped schemas)
- Frontend: React SPA served by Express
- Prover: Circom 2 + Rust (snarkjs / Nova)
- Verifier: zkSync Era Sepolia (BN254 Groth16)
- Deployment: Render (web + worker) + Kubernetes support for enterprise/air-gapped
- Monitoring: Render health checks, live metrics panels
- Email: Postmark

## Key Endpoints (Live)

- `GET /health` — System health
- `POST /api/auth/signup` — User + API key
- `GET /api/live-metrics/context-integrity` — Immutability Shield
- `GET /api/live-metrics/consistency` — Adversarial Challenge Shield
- `POST /api/demo/complete` — Triggers nurture sequence
- `/demo/live-bidding` — Live Coalition Market Auction visualization
- `/trust` — Five Shields trust framework

## Deployment (Single-Repo Era)

All code lives in this repository (`stephentrembley-oss/Sturna.ai`).

Push to `main` → triggers Render deploy (or enterprise k8s pipeline).

See `docs/DEPLOYMENT_AND_MIRROR_WORKFLOW.md` for the current (updated) process. The previous dual-repo mirror to Polsia-Inc/octomind is deprecated.

## Documentation

- `docs/MASTER_IMPLEMENTATION_DOCUMENT.md` — Full v2.2 architecture, roadmap, GTM
- `docs/BRAND_VOICE_AND_IDENTITY_GUIDELINES.md` — Exact voice, lexicon, what to say/avoid
- `docs/MARKET_AND_CUSTOMER_INTELLIGENCE.md` — Buyer personas, outreach templates, competitive landscape, revenue projections
- `docs/DEPLOYMENT_AND_MIRROR_WORKFLOW.md` — Current deployment & ops process
- `circuits/` & `contracts/` — zk-SNARK compliance circuit + Groth16 verifier
- `octomind/` — Core biomimetic orchestration layer (ShivaLimbOrchestrator, agent utilities, selected services)

## Quick Start (Local)

```bash
git clone https://github.com/stephentrembley-oss/Sturna.ai.git
cd Sturna.ai
# Install deps (Node + Python components)
npm install && pip install -r requirements.txt
npm run migrate
npm run dev
```

Health check: `curl http://localhost:PORT/health` → 200 OK

## Current Status (May 2026)

- PH Launch: May 21, 2026 — live
- RIA Pilot: June 3, 2026 target
- SOC 2 Type II: In progress (Day 134/180)
- Daily lead gen: 50-75 qualified (RIAs + Healthcare + SaaS)
- First paying customer target: Within 30 days

The product is complete. The only thing that matters now is getting compliance buyers to experience the free scanners and see the verifiable evidence firsthand.

---

**Built for teams that must prove every AI decision.**

Live: https://octomind-9fce.polsia.app (Render service)