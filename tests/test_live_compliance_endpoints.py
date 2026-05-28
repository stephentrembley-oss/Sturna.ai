import httpx
import time
from datetime import datetime, timedelta

BASE_URL = "https://sturna-ai-s862.onrender.com"


def run_live_tests():
    print("\n" + "="*60)
    print("Sturna.ai Live Compliance Endpoint Tests")
    print("="*60)

    client = httpx.Client(base_url=BASE_URL, timeout=45.0)
    results = []

    def test(name, func):
        try:
            func(client)
            print(f"[PASS] {name}")
            results.append((name, True))
        except Exception as e:
            print(f"[FAIL] {name}")
            print(f"       Error: {e}")
            results.append((name, False))

    # Test 1: Health
    def health_check(c):
        r = c.get("/")
        assert r.status_code == 200
        assert "Sturna.ai" in r.text
    test("Health Check", health_check)

    # Test 2: Register AI System
    system_id = f"test-sys-{int(time.time())}"
    def register_ai_system(c):
        payload = {
            "system_id": system_id,
            "name": "Live Test Credit Agent",
            "description": "Automated credit scoring - live test",
            "risk_level": "high",
            "owner": "test-team"
        }
        r = c.post("/api/v1/ai-inventory/register", json=payload)
        assert r.status_code == 200
        assert r.json()["system_id"] == system_id
    test("Register AI System", register_ai_system)

    # Test 3: List AI Systems
    def list_ai_systems(c):
        r = c.get("/api/v1/ai-inventory/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
    test("List AI Systems", list_ai_systems)

    # Test 4: NIST Report
    def nist_report(c):
        r = c.get("/api/v1/ai-inventory/nist-report")
        assert r.status_code == 200
        data = r.json()
        assert "total_systems" in data
    test("NIST Report", nist_report)

    # Test 5: Log Human Review
    task_id = f"task-live-{int(time.time())}"
    def log_review(c):
        payload = {
            "task_id": task_id,
            "agent_id": "agent-live-001",
            "decision": "approve",
            "reviewer_id": "compliance-tester",
            "justification": "Approved during automated live testing",
            "reviewer_role": "CCO"
        }
        r = c.post("/api/v1/reviews/", json=payload)
        assert r.status_code == 200
        assert r.json()["decision"] == "approve"
    test("Log Human Review Decision", log_review)

    # Test 6: Get Pending Reviews
    def pending_reviews(c):
        r = c.get("/api/v1/reviews/pending")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
    test("Get Pending Reviews", pending_reviews)

    # Test 7: Generate Evidence Package
    def generate_evidence(c):
        now = datetime.utcnow()
        params = {
            "framework": "soc2",
            "period_start": (now - timedelta(days=7)).isoformat(),
            "period_end": now.isoformat(),
            "generated_by": "live-test-bot"
        }
        r = c.post("/api/v1/evidence/generate", params=params)
        assert r.status_code == 200
        data = r.json()
        assert "package_id" in data
    test("Generate Evidence Package", generate_evidence)

    # Summary
    print("\n" + "="*60)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    if passed == total:
        print("All live compliance endpoints are working!")
    else:
        print("Some tests failed. Check the logs above.")
    print("="*60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_live_tests()
    exit(0 if success else 1)
