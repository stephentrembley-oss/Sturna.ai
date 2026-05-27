# Octomind Layer

Biomimetic multi-agent orchestration layer for Sturna.ai.

## Purpose
Provides self-healing, coalition-based agent orchestration with strong compliance and verifiability features.

## Current Status (May 2026)

- Large number of services imported from `octomind.zip`
- Core biomimetic, coalition, compliance, and intent/memory services are present
- Many services are intentionally lightweight (service interfaces + placeholders)
- Full integration and hardening is ongoing

## Layer Philosophy

The Octomind layer follows a **biomimetic + compliance-first** design:

- Services are designed as small, focused, replaceable units
- Many start as structured placeholders that can be expanded
- Emphasis on auditability, self-healing, and coalition coordination

## Key Components

### Biomimetic Core
- `ShivaLimbOrchestrator` — Limb lifecycle, regeneration, checkpointing
- `OctopusNeuralLayer` — Distributed autonomy
- `SelfHealingRouter`, `CrisprAgentEditor`, `CephalopodRecoder`

### Coalition & Auction System
- `CoalitionEngine` + supporting services

### Compliance & Governance
- `ControlHarmonization`, `CompliancePolygraph`, `MARCH` / `GSAR` gates

### Intent & Memory
- `IntentEngine`, memory consolidation, anomaly detection

## Usage

```js
const {
  ShivaLimbOrchestrator,
  CoalitionEngine,
  ControlHarmonization
} = require('./octomind/services');
```

## Contributing

See the root `CONTRIBUTING.md`. When working on Octomind services, prefer small, focused modules with clear ownership comments.