from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.compliance.soc2_evidence_service import SOC2EvidenceService
from app.schemas.evidence import EvidencePackageOut


router = APIRouter(prefix="/api/v1/evidence", tags=["Compliance Evidence"])


@router.post("/generate", response_model=EvidencePackageOut, summary="Generate a compliance evidence package")
def generate_evidence_package(
    framework: str = Query("soc2", description="soc2, eu_ai_act, hipaa, etc."),
    period_start: datetime = Query(...),
    period_end: datetime = Query(...),
    generated_by: str = Query(...),
    db: Session = Depends(get_db),
):
    service = SOC2EvidenceService(db)
    return service.generate_package(framework, period_start, period_end, generated_by)


@router.get("/{package_id}", response_model=EvidencePackageOut)
def get_evidence_package(package_id: str, db: Session = Depends(get_db)):
    from app.models.evidence_package import EvidencePackage
    pkg = db.query(EvidencePackage).filter_by(package_id=package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Evidence package not found")
    return pkg
