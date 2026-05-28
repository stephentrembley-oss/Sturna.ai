import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.human_review import HumanReviewLog
from app.compliance.human_review_service import HumanReviewService


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_log_decision_creates_record(db_session):
    service = HumanReviewService(db_session)
    log = service.log_decision(
        task_id="task-123",
        agent_id="agent-456",
        decision="approve",
        reviewer_id="reviewer-1",
        justification="Looks good",
    )
    assert log.decision_id is not None
    assert log.task_id == "task-123"
    assert log.decision == "approve"
    assert log.chain_hash is not None


def test_chain_integrity(db_session):
    service = HumanReviewService(db_session)

    log1 = service.log_decision("task-1", "agent-1", "approve", "rev-1")
    log2 = service.log_decision(
        "task-1", "agent-1", "approve", "rev-1", previous_decision_id=log1.decision_id
    )

    is_valid = service.verify_chain_integrity("task-1")
    assert is_valid is True


def test_pending_reviews(db_session):
    service = HumanReviewService(db_session)
    service.log_decision("task-2", "agent-2", "escalate", "rev-2")

    pending = service.get_pending_reviews()
    assert len(pending) >= 1
    assert pending[0].is_pending is True
