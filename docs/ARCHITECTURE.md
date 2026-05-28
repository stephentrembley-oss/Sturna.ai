# Sturna.ai Architecture Overview

## High-Level Design

Sturna.ai is a **compliance-first, self-healing multi-agent execution platform** designed for regulated industries (finance/RIAs, healthcare, legal).

Core philosophy: **"The best specialized intelligence always wins, and every win is provably correct."**

## Key Layers

### 1. Core Runtime (Python / FastAPI)
- Main API server (`main.py`)
- FastAPI + PostgreSQL (Neon)
- Authentication, user management, demo flows

### 2. Octomind Layer (Biomimetic Agent Orchestration)
- Located in `octomind/`
- `ShivaLimbOrchestrator`: Self-healing limb management and regeneration
- `OctopusNeuralLayer`: Distributed autonomy inspired by cephalopod biology
- Coalition Market Auction system (446+ specialist agents)
- Intent engine, memory layer, quality gates

### 3. Compliance & Governance Layer
- `ControlHarmonization`
- MARCH and GSAR pipelines
- WORM audit trails (SEC 17a-4 ready)
- zk-SNARK verifiable execution
- Regulatory Policy Graph

### 4. Cryptographic Moat
- Circom circuits (`circuits/`)
- Groth16 verifier on zkSync Era (`contracts/`)
- Poseidon hash, Nova folding

### 5. Deployment
- Primary: Render (web + worker)
- Enterprise: Kubernetes (`k8s/`)

## Data Flow (Simplified)

1. Task arrives (via API or demo)
2. Intent classification & decomposition
3. Coalition Market Auction (agents bid with confidence + compliance)
4. Winning agent executes
5. Quality gates (MARCH) + adversarial review
6. zk-SNARK proof generated
7. WORM audit log written
8. Result + proof returned to user

## Key Design Principles

- **Evidence-first**: Every claim must be backed by signed, verifiable proof.
- **Self-healing**: Automatic failover and coalition reformation.
- **Compliance by design**: Built for SOC 2, HIPAA, EU AI Act, Reg S-P from day one.
- **Lightweight services**: Many Octomind services start as focused interfaces that can be expanded.

## Repository Structure

- `main.py` + `lib/` — Core FastAPI application
- `octomind/` — Biomimetic agent layer
- `circuits/` + `contracts/` — zk-SNARK compliance layer
- `k8s/` — Kubernetes manifests
- `docs/` — Documentation

For detailed implementation, see `docs/MASTER_IMPLEMENTATION_DOCUMENT.md`.