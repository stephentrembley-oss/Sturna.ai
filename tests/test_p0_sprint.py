"""
Sturna.ai P0 Sprint Tests
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_pilot_signup_validation():
    response = client.post("/api/pilot/signup", json={})
    assert response.status_code == 422

def test_trust_shields():
    response = client.get("/api/trust/shields")
    assert response.status_code == 200
    data = response.json()
    assert "overall_status" in data
    assert "shields" in data