from sqlalchemy import Column, String, DateTime, JSON, Integer, Text
from app.models.base import Base
from datetime import datetime, timezone


class EvidencePackage(Base):
    __tablename__ = "evidence_packages"

    id = Column(Integer, primary_key=True)
    package_id = Column(String(64), unique=True, index=True, nullable=False)
    framework = Column(String(50), nullable=False)          # soc2, eu_ai_act, hipaa, etc.
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    evidence_json = Column(JSON, nullable=False)
    integrity_hash = Column(String(128), nullable=False)
    generated_by = Column(String(64))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<EvidencePackage {self.package_id} framework={self.framework}>"
