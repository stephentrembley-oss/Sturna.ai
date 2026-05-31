"""Health check endpoints for Sturna.ai."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    """Liveness probe — always 200 if service is running."""
    return {"status": "ok", "service": "sturna", "phase": 2}


@router.get("/ready")
async def ready():
    """Readiness probe — checks core engine initialization."""
    from app.core.intent_engine import get_intent_engine
    try:
        engine = get_intent_engine()
        ready = (
            engine.galaxy_manager is not None and
            engine.dag_scheduler is not None and
            engine.grounding_gate is not None
        )
        return {
            "status": "ready" if ready else "initializing",
            "checks": {
                "intent_engine": "ok",
                "galaxy_manager": "ok" if engine.galaxy_manager else "missing",
                "dag_scheduler": "ok" if engine.dag_scheduler else "missing",
                "grounding_gate": "ok" if engine.grounding_gate else "missing",
            }
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@router.get("/healthz")
async def healthz():
    """Backwards-compatible health endpoint."""
    return await health()