from sqlalchemy import Column, String, DateTime, JSON, Integer, Text, Boolean
from app.models.base import Base
from datetime import datetime, timezone


class AISystem(Base):
    __tablename__ = "ai_systems"

    id = Column(Integer, primary_key=True)
    system_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    risk_level = Column(String(20), nullable=False)          # minimal, limited, high, prohibited
    owner = Column(String(64), nullable=False)
    eu_ai_act_high_risk = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "system_id": self.system_id,
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level,
            "owner": self.owner,
            "eu_ai_act_high_risk": self.eu_ai_act_high_risk,
            "metadata": self.metadata_json or {},
        }
