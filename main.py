from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from app.orchestration.shiva_limb_orchestrator import ShivaLimbOrchestrator
from lib.post_quantum_gateway import PostQuantumGateway
from lib.xai_explainability import XAIExplainability

app = FastAPI(title="Sturna.ai", description="Compliance Intelligence Platform powered by biomimetic auction agents")

# Mock DB and Redis for pilot (in-memory)
mock_db = {}
mock_redis = None  # Placeholder

orchestrator = ShivaLimbOrchestrator(db_session=mock_db, redis_client=mock_redis)
pqc_gateway = PostQuantumGateway()
xai = XAIExplainability()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ComplianceIntent(BaseModel):
    agent_id: str = "ria_pilot_001"
    intent_data: Dict[str, Any]

@app.get("/")
def root():
    return {"message": "✅ Sturna.ai RIA Pilot v0 is LIVE on feature/ria-pilot-v0!", "status": "healthy", "pilot": "Reg S-P Compliance Demo"}

@app.get("/health")
def health():
    return {"status": "ok", "version": "pilot-v0"}

@app.post("/api/v1/process-compliance-intent")
async def process_compliance_intent(intent: ComplianceIntent):
    try:
        result = orchestrator.process_intent(
            agent_id=intent.agent_id,
            intent_data=intent.intent_data
        )
        # Add PQC hardening and XAI
        result = pqc_gateway.harden_for_compliance(result)
        result["xai_explanation"] = xai.generate_model_card(result.get("decision", {}), intent.intent_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
