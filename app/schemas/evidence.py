from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EvidencePackageCreate(BaseModel):
    framework: str
    period_start: datetime
    period_end: datetime
    generated_by: str


class EvidencePackageOut(BaseModel):
    package_id: str
    framework: str
    period_start: Optional[datetime]
    period_end: Optional[datetime]
    evidence_json: Dict[str, Any]
    integrity_hash: str
    generated_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
