import httpx
import pytest
from datetime import datetime, timedelta

BASE_URL = "https://sturna-ai-s862.onrender.com"

client = httpx.Client(base_url=BASE_URL, timeout=30.0)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert "Sturna.ai" in response.text


def test_register_ai_system():
    payload = {
        "system_id": f"test-sys-{datetime.now().timestamp()}",
        "name": "Test Credit Agent",
        "description": "Automated credit scoring for testing",
        "risk_level": "high",
        "owner": "test-team"
    }
    response = client.post("/api/v1/ai-inventory/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["system_id"] == payload["system_id"]


def test_list_ai_systems():
    response = client.get("/api/v1/ai-inventory/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_nist_report():
    response = client.get("/api/v1/ai-inventory/nist-report")
    assert response.status_code == 200
    data = response.json()
    assert "total_systems" in data


def test_log_human_review():
    payload = {
        "task_id": f"task-live-{datetime.now().timestamp()}",
        "agent_id": "agent-live-001",
        "decision": "approve",
        "reviewer_id": "compliance-tester",
        "justification": "Approved during live testing",
        "reviewer_role": "CCO"
    }
    response = client.post("/api/v1/reviews/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "approve"


def test_get_pending_reviews():
    response = client.get("/api/v1/reviews/pending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_generate_evidence_package():
    now = datetime.utcnow()
    params = {
        "framework": "soc2",
        "period_start": (now - timedelta(days=7)).isoformat(),
        "period_end": now.isoformat(),
        "generated_by": "live-test-bot"
    }
    response = client.post("/api/v1/evidence/generate", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "package_id" in data


if __name__ == "__main__":
    import subprocess
    import sys
    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    sys.exit(result.returncode)
