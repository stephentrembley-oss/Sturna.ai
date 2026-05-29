from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from app.database import Base
import enum


class PilotStatus(str, enum.Enum):
    SIGNED_UP = "signed_up"
    WORKSPACE_PROVISIONED = "workspace_provisioned"
    SCAN_COMPLETED = "scan_completed"
    EVIDENCE_GENERATED = "evidence_generated"
    WALKTHROUGH_SCHEDULED = "walkthrough_scheduled"
    WALKTHROUGH_COMPLETED = "walkthrough_completed"
    PILOT_COMPLETED = "pilot_completed"
    CONVERTED = "converted"
    EXPIRED = "expired"


class PilotAccount(Base):
    __tablename__ = "pilot_accounts"

    id = Column(Integer, primary_key=True, index=True)
    pilot_id = Column(String(100), unique=True, index=True)
    company_name = Column(String(200))
    contact_first_name = Column(String(100))
    contact_last_name = Column(String(100))
    contact_email = Column(String(255), index=True)
    contact_title = Column(String(200))
    company_size = Column(String(50))
    primary_framework = Column(String(50))
    current_compliance_state = Column(String(50))
    urgency_level = Column(String(50))
    referral_source = Column(String(200))
    notes = Column(Text)

    status = Column(String(50), default=PilotStatus.SIGNED_UP)
    compliance_score = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    converted_at = Column(DateTime)

    def __repr__(self):
        return f"<PilotAccount {self.pilot_id} ({self.company_name})>"