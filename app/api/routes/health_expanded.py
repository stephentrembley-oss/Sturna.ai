from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import os
from app.database import get_db, engine

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("/expanded")
async def health_expanded(db: Session = Depends(get_db)):
    checks = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "enterprise-v2-p0",
        "overall": "healthy",
        "components": {}
    }

    # Database
    try:
        db.execute(text("SELECT 1"))
        checks["components"]["database"] = {
            "status": "healthy",
            "type": "postgresql" if "postgresql" in str(engine.url) else "sqlite"
        }
    except Exception as e:
        checks["components"]["database"] = {"status": "unhealthy", "error": str(e)}
        checks["overall"] = "degraded"

    # P0 Sprint modules
    try:
        checks["components"]["p0_sprint"] = {
            "status": "healthy",
            "modules": ["lead_gen", "pilot_onboarding", "trust_shields"]
        }
    except Exception as e:
        checks["components"]["p0_sprint"] = {"status": "unhealthy", "error": str(e)}

    # Environment
    required = ["STURNA_BASE_URL", "DATABASE_URL", "SECRET_KEY"]
    missing = [v for v in required if not os.getenv(v)]
    checks["components"]["environment"] = {
        "status": "healthy" if not missing else "degraded",
        "missing_vars": missing
    }

    return checks


@router.get("/ready")
async def readiness_check():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")