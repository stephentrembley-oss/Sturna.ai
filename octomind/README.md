# Octomind Layer

Biomimetic multi-agent orchestration layer extracted from octomind.zip (May 2026).

## Purpose
Provides self-healing, coalition-based task routing with strong compliance and verifiability features for Sturna.ai.

## Key Components
- **Biomimetic Core**: ShivaLimbOrchestrator, OctopusNeuralLayer, SelfHealingRouter, CrisprAgentEditor, CephalopodRecoder
- **Coalition Auction System**: CoalitionEngine, CoalitionClearing, CoalitionPerformance, etc.
- **Compliance & Governance**: ControlHarmonization, CompliancePolygraph, MARCH/GSAR gates, RegulatoryPolicyGraph
- **Intent & Memory**: IntentEngine, Memory services

## Current Status (as of May 26, 2026)

- Large number of services from octomind.zip have been imported into `octomind/services/`
- Many core services have been cleaned up and given proper structure
- `services/index.js` barrel file created for convenient importing
- Significant cleanup and documentation work completed
- Layer is actively being integrated into the main Sturna.ai codebase

## Usage
```js
const { 
  ShivaLimbOrchestrator, 
  CoalitionEngine, 
  ControlHarmonization 
} = require('./octomind/services');
```

See `services/index.js` for the current list of exported services.
