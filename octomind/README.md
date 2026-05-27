# Octomind Layer

This directory contains the biomimetic multi-agent orchestration layer extracted from `octomind.zip` (May 2026).

## Purpose

Provides the core self-healing, coalition-based, and compliance-aware agent infrastructure for Sturna.ai, including:

- **ShivaLimbOrchestrator** — Limb regeneration, checkpointing, and self-healing
- **Octopus Neural Layer** — Distributed autonomy and 4D coalition scoring
- **Coalition Market Auction** engine
- **MARCH / GSAR / Control Harmonization** compliance gates
- Large library of specialized agent services

## Structure

- `services/` — Individual service modules (170+ files)
- `index.js` — Barrel file for easy importing of key services

## Origin

Extracted from the `octomind.zip` archive in Google Drive. This layer was previously part of the (now deprecated) dual-repo setup with Polsia-Inc/octomind.

## Usage

```js
const {
  ShivaLimbOrchestrator,
  CoalitionEngine,
  ControlHarmonization
} = require('./octomind/services');
```

Most services can also be required directly when needed.

## Status

This layer is actively being integrated into the main Sturna.ai codebase (May 2026).
