# Sturna.ai - Compliance Intelligence Platform

**Live RIA Pilot v0** (feature/ria-pilot-v0 branch)

Compliance Intelligence powered by **biomimetic auction agents** (Shiva-Octopus inspired).

## Quick Start - Working Pilot Demo

1. Clone & checkout branch:
   ```bash
   git checkout feature/ria-pilot-v0
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. Test the pilot endpoint:
   ```bash
   curl -X POST http://localhost:8000/api/v1/process-compliance-intent \
     -H "Content-Type: application/json" \
     -d '{
       "agent_id": "ria_pilot_001",
       "intent_data": {
         "query": "How to handle client email with PII under Reg S-P?"
       }
     }'
   ```

**Expected output**: Full JSON with winning agent, compliance decision, risk score, ZK proof, limb regeneration status, PQC hardening + XAI.

## Features in Pilot
- Biomimetic agent auction (4 specialized agents)
- Reg S-P RIA compliance simulation
- Post-quantum crypto gateway
- Self-improving limb regeneration
- Groth16 ZK proof mock
- XAI model card

Full vision: 446 agents, full meta-learning, autonomous regulatory monitoring.

Deployed to Render - live at your Render URL.

Made for rapid iteration toward production pilot launch.