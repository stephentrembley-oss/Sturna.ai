from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer, Text
from app.models.base import Base
from datetime import datetime, timezone


class HumanReviewLog(Base):
    __tablename__ = "human_review_logs"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String(64), unique=True, index=True, nullable=False)
    task_id = Column(String(64), index=True, nullable=False)
    agent_id = Column(String(64), index=True, nullable=False)
    decision = Column(String(20), nullable=False)           # approve / reject / modify / escalate
    justification = Column(Text, nullable=True)
    reviewer_id = Column(String(64), nullable=False)
    reviewer_role = Column(String(50), nullable=True)
    previous_decision_id = Column(String(64), nullable=True)
    chain_hash = Column(String(128), nullable=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_pending = Column(Boolean, default=False, index=True)

    def __repr__(self):
        return f"<HumanReviewLog {self.decision_id} decision={self.decision}>"
