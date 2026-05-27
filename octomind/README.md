# Octomind Services Layer

This directory contains the **biomimetic multi-agent orchestration layer** extracted from `octomind.zip` (May 2026).

## Overview

The Octomind layer provides Sturna.ai with:

- Self-healing agent orchestration (ShivaLimbOrchestrator)
- Distributed neural architecture inspired by octopus biology
- Coalition Market Auction system for task routing
- Strong compliance & governance primitives (MARCH, GSAR, Control Harmonization)
- Large library of specialized agent services

## Directory Structure

- `services/` — Individual service modules (~170+ files)
- `index.js` — Barrel file for convenient importing of key services

## Key Services

### Core Biomimetic
- `ShivaLimbOrchestrator` — Limb lifecycle, regeneration, checkpointing
- `OctopusNeuralLayer` — Suckerotopy, distributed autonomy
- `SelfHealingRouter` — Automatic failover and coalition reformation
- `CrisprAgentEditor` — Meta-adaptation / agent editing
- `CephalopodRecoder` — RNA-style self-editing layer

### Coalition & Auction
- `CoalitionEngine`
- `CoalitionClearing`
- `CoalitionPerformance`

### Compliance & Governance
- `ControlHarmonization` (Gold Nugget)
- `CompliancePolygraph`
- `FederatedComplianceNetwork`
- `RegulatoryPolicyGraph`

### Quality & Safety
- `QualityGates`
- `MarchCheckerConfig` / `MarchAdversarial`
- `ConstitutionalFilter`
- `GSARRecovery`

## Usage

```js
const { 
  ShivaLimbOrchestrator, 
  CoalitionEngine, 
  ControlHarmonization 
} = require('./octomind/services');
```

You can also require services directly:
```js
const MarchConfig = require('./octomind/services/march-checker-config');
```

## Origin & Status

Extracted from the `octomind.zip` archive. This layer was previously maintained in the (now deprecated) dual-repo workflow. It is currently being integrated into the main `Sturna.ai` codebase (May 2026).

## Notes

Many services contain detailed JSDoc-style comments explaining ownership and responsibilities. This layer forms the foundation of Sturna’s self-healing and verifiable agent execution capabilities.