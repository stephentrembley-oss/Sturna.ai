from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.compliance.ai_system_inventory import AISystemInventory, RiskLevel


router = APIRouter(prefix="/api/v1/ai-inventory", tags=["AI System Inventory"])

# In-memory instance for now (can be replaced with DB-backed later)
inventory = AISystemInventory()


@router.post("/register", summary="Register a new AI system")
def register_system(
    system_id: str = Query(...),
    name: str = Query(...),
    description: str = Query(...),
    risk_level: RiskLevel = Query(RiskLevel.HIGH),
    owner: str = Query(...),
):
    return inventory.register_system(
        system_id=system_id,
        name=name,
        description=description,
        risk_level=risk_level,
        owner=owner,
    )


@router.get("/", summary="List all registered AI systems")
def list_systems(risk_level: Optional[RiskLevel] = None):
    return inventory.list_systems(risk_level)


@router.get("/nist-report", summary="Generate NIST AI RMF style report")
def get_nist_report():
    return inventory.generate_nist_report()
