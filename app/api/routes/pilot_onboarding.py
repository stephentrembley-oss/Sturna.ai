from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime, timedelta
import os
from app.database import get_db
from app.models.pilot import PilotAccount, PilotStatus

router = APIRouter(prefix="/api/pilot", tags=["RIA Pilot"])


class PilotSignupRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    contact_first_name: str = Field(..., min_length=1, max_length=100)
    contact_last_name: str = Field(..., min_length=1, max_length=100)
    contact_email: EmailStr
    contact_title: str
    company_size: Literal["1-10", "11-50", "51-200", "201-500", "500+"]
    primary_framework: Literal["Reg_S_P", "SEC_17a_4", "HIPAA", "SOC_2", "EU_AI_Act", "Multiple"]
    urgency_level: Literal["June_3_deadline", "Next_30_days", "Next_quarter", "Exploratory"]
    referral_source: Optional[str] = None
    notes: Optional[str] = None


@router.post("/signup", response_model=dict)
async def pilot_signup(
    request: PilotSignupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    existing = db.query(PilotAccount).filter(
        PilotAccount.contact_email == request.contact_email
    ).first()

    if existing:
        return {
            "success": True,
            "pilot_id": existing.pilot_id,
            "status": existing.status,
            "message": "Pilot already exists",
            "workspace_url": f"/pilot/workspace?pid={existing.pilot_id}"
        }

    pilot_id = f"RIA_{datetime.utcnow().strftime('%Y%m%d')}_{os.urandom(3).hex().upper()}"

    pilot = PilotAccount(
        pilot_id=pilot_id,
        company_name=request.company_name,
        contact_first_name=request.contact_first_name,
        contact_last_name=request.contact_last_name,
        contact_email=request.contact_email,
        contact_title=request.contact_title,
        company_size=request.company_size,
        primary_framework=request.primary_framework,
        urgency_level=request.urgency_level,
        referral_source=request.referral_source,
        notes=request.notes,
        status=PilotStatus.SIGNED_UP,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=14)
    )

    db.add(pilot)
    db.commit()
    db.refresh(pilot)

    background_tasks.add_task(_provision_workspace, pilot_id)
    background_tasks.add_task(_send_welcome_nurture, pilot_id, request.contact_email)

    if request.urgency_level == "June_3_deadline":
        background_tasks.add_task(_flag_priority_pilot, pilot_id)

    return {
        "success": True,
        "pilot_id": pilot_id,
        "status": "signed_up",
        "workspace_url": f"/pilot/workspace?pid={pilot_id}",
        "expires_at": pilot.expires_at.isoformat()
    }


@router.get("/workspace/{pilot_id}", response_model=dict)
async def get_pilot_workspace(pilot_id: str, db: Session = Depends(get_db)):
    pilot = db.query(PilotAccount).filter(PilotAccount.pilot_id == pilot_id).first()
    if not pilot:
        raise HTTPException(status_code=404, detail="Pilot not found")

    return {
        "pilot_id": pilot_id,
        "company_name": pilot.company_name,
        "status": pilot.status,
        "days_remaining": (pilot.expires_at - datetime.utcnow()).days,
        "primary_framework": pilot.primary_framework,
        "compliance_score": pilot.compliance_score or 0
    }


async def _provision_workspace(pilot_id: str):
    print(f"[Pilot] Workspace provisioned for {pilot_id}")


async def _send_welcome_nurture(pilot_id: str, email: str):
    print(f"[Pilot] Welcome nurture triggered for {pilot_id}")


async def _flag_priority_pilot(pilot_id: str):
    print(f"[Pilot] PRIORITY FLAG: {pilot_id} - June 3 deadline")