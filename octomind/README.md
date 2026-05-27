# Octomind Layer

Biomimetic multi-agent orchestration layer extracted from octomind.zip.

## Purpose
Provides self-healing, coalition-based task routing with strong compliance and verifiability features.

## Key Components
- **Biomimetic Core**: ShivaLimbOrchestrator, OctopusNeuralLayer, SelfHealingRouter
- **Coalition Auction System**: CoalitionEngine, CoalitionClearing, etc.
- **Compliance Layer**: ControlHarmonization, CompliancePolygraph, MARCH/GSAR gates
- **Intent & Memory**: IntentEngine, Memory services

## Usage
```js
const services = require('./octomind/services');
const orchestrator = new services.ShivaLimbOrchestrator();
```

See `services/index.js` for the full list of exported services.
