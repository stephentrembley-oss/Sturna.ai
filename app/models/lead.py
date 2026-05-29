from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from datetime import datetime
from app.database import Base
import enum


class LeadSource(str, enum.Enum):
    LINKEDIN = "linkedin"
    REDDIT = "reddit"
    WEBSITE = "website"
    REFERRAL = "referral"
    PRODUCT_HUNT = "product_hunt"
    PILOT_SIGNUP = "pilot_signup"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    DEMO_SCHEDULED = "demo_scheduled"
    DEMO_COMPLETED = "demo_completed"
    PILOT_SIGNED = "pilot_signed"
    CONVERTED = "converted"
    LOST = "lost"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), default=LeadSource.WEBSITE)
    status = Column(String(50), default=LeadStatus.NEW)

    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), index=True)
    title = Column(String(200))
    company = Column(String(200))
    industry = Column(String(50))
    company_size = Column(String(50))
    linkedin_url = Column(String(500))

    campaign_name = Column(String(200))
    priority_score = Column(Integer, default=50)

    notes = Column(Text)
    metadata_json = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    scored_at = Column(DateTime)
    last_engagement = Column(DateTime)

    demo_completed = Column(Boolean, default=False)
    scanner_used = Column(Boolean, default=False)
    evidence_downloaded = Column(Boolean, default=False)
    pilot_signed = Column(Boolean, default=False)

    emails_opened = Column(Integer, default=0)
    nurture_trigger_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Lead {self.email} ({self.company})>"