from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.compliance.ai_system_inventory import AISystemInventory


router = APIRouter(prefix="/api/v1/ai-inventory", tags=["AI System Inventory"])


@router.post("/register", summary="Register or update an AI system")
def register_system(
    system_id: str = Query(...),
    name: str = Query(...),
    description: str = Query(""),
    risk_level: str = Query("high"),
    owner: str = Query(...),
    db: Session = Depends(get_db),
):
    inventory = AISystemInventory(db)
    return inventory.register_system(
        system_id=system_id,
        name=name,
        description=description,
        risk_level=risk_level,
        owner=owner,
    )


@router.get("/", summary="List registered AI systems")
def list_systems(
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    inventory = AISystemInventory(db)
    return inventory.list_systems(risk_level)


@router.get("/nist-report", summary="Generate NIST-style report")
def get_nist_report(db: Session = Depends(get_db)):
    inventory = AISystemInventory(db)
    return inventory.generate_nist_report()
