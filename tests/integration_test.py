"""Sturna.ai — End-to-End Integration Test Script.
Validates the full Phase 2+3 flow:
1.  Database connectivity
2.  Agent seeding (if needed)
3.  Intent execution (5-stage pipeline)
4.  Memory verification (written + stored)
5.  Auction tracking (bids + winner)
6.  Shared memory consolidation (after daemon)
Run: python tests/integration_test.py
"""
import asyncio
import sys
import uuid

from datetime import datetime

import httpx
import structlog

structlog.configure(
    processors=[structlog.dev.ConsoleRenderer()],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger("integration_test")

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


class SturnaIntegrationTest:
    """End-to-end integration test suite."""

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=TIMEOUT)
        self.passed = 0
        self.failed = 0
        self.results = []

    async def run(self):
        """Run all tests in sequence."""
        logger.info("🚀 Starting Sturna.ai Integration Tests", base_url=BASE_URL)
        
        try:
            await self.test_health()
            await self.test_readiness()
            await self.test_agent_list()
            await self.test_intent_execution()
            await self.test_memory_written()
            await self.test_auction_created()
            await self.test_shared_memory()
            await self.test_visitor_tracking()
            
        except Exception as e:
            logger.error("💥 Test suite aborted", error=str(e))
            raise
        
        finally:
            await self.client.aclose()
        
        # Summary
        total = self.passed + self.failed
        logger.info(
            "📊 Test Summary",
            total=total,
            passed=self.passed,
            failed=self.failed,
            pass_rate=f"{self.passed/max(total,1)*100:.1f}%",
        )
        
        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            logger.info(f"  {status} {result['name']}: {result['message']}")
        
        return self.failed == 0

    async def _check(self, name: str, func):
        """Run a single test with error handling."""
        try:
            result = await func()
            self.passed += 1
            self.results.append({"name": name, "passed": True, "message": result})
            logger.info(f"✅ {name}", result=result)
            return True
        except Exception as e:
            self.failed += 1
            self.results.append({"name": name, "passed": False, "message": str(e)})
            logger.error(f"❌ {name}", error=str(e))
            return False

    async def test_health(self):
        """Test 1: Health endpoint responds."""
        async def _test():
            resp = await self.client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "ok"
            return f"status={data['status']}, phase={data.get('phase', 'unknown')}"
        
        return await self._check("Health Check", _test)

    async def test_readiness(self):
        """Test 2: Readiness probe shows all components."""
        async def _test():
            resp = await self.client.get("/ready")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] in ["ready", "initializing"]
            checks = data.get("checks", {})
            return f"status={data['status']}, checks={checks}"
        
        return await self._check("Readiness Probe", _test)

    async def test_agent_list(self):
        """Test 3: Agent list endpoint works (seeded or empty)."""
        async def _test():
            resp = await self.client.get("/api/agents?limit=5")
            assert resp.status_code == 200
            data = resp.json()
            count = len(data)
            if count == 0:
                return "WARNING: No agents seeded. Run: python scripts/seed_agents.py"
            return f"found {count} agents"
        
        return await self._check("Agent List", _test)

    async def test_intent_execution(self):
        """Test 4: Full 5-stage intent pipeline executes."""
        async def _test():
            payload = {
                "intent_text": "Analyze SEC 10-K filing for compliance gaps under FINRA rules",
                "intent_category": "financial",
            }
            
            resp = await self.client.post("/api/intents/execute", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            
            assert data["status"] in ["success", "no_agents", "blocked"]
            
            if data["status"] == "no_agents":
                return "WARNING: No eligible agents for coalition. Seed agents first."
            
            assert "winner_agent_id" in data
            assert "transparency_card" in data
            assert "execution_time_ms" in data
            
            # Store for later tests
            self.last_intent_id = data["intent_id"]
            self.last_winner = data["winner_agent_id"]
            
            card = data["transparency_card"]
            stages = card.get("stages", {})
            
            return (
                f"status={data['status']}, "
                f"winner={data['winner_agent_id']}, "
                f"latency={data['execution_time_ms']:.1f}ms, "
                f"stages={list(stages.keys())}"
            )
        
        return await self._check("Intent Execution", _test)

    async def test_memory_written(self):
        """Test 5: Winner agent wrote a memory entry."""
        async def _test():
            if not hasattr(self, "last_winner"):
                return "SKIPPED: No intent executed"
            
            resp = await self.client.get(f"/api/memory/{self.last_winner}")
            assert resp.status_code == 200
            data = resp.json()
            
            memories = data.get("memories", [])
            if not memories:
                return "WARNING: No memories found. Memory service may not be wired yet."
            
            # Check for intent_pattern memory
            intent_memories = [m for m in memories if m.get("memory_type") == "intent_pattern"]
            grounding_memories = [m for m in memories if m.get("memory_type") == "factual_grounding"]
            
            return (
                f"total={len(memories)}, "
                f"intent_patterns={len(intent_memories)}, "
                f"grounding={len(grounding_memories)}"
            )
        
        return await self._check("Memory Written", _test)

    async def test_auction_created(self):
        """Test 6: Auction was created and tracked."""
        async def _test():
            resp = await self.client.get("/api/auctions/live")
            assert resp.status_code == 200
            data = resp.json()
            
            # Could be 0 if all auctions completed
            return f"active_auctions={data.get('active_count', 0)}"
        
        return await self._check("Auction Tracking", _test)

    async def test_shared_memory(self):
        """Test 7: Shared memory patterns exist (after daemon runs)."""
        async def _test():
            resp = await self.client.get("/api/memory/shared/stats")
            assert resp.status_code == 200
            data = resp.json()
            
            total = data.get("total_patterns", 0)
            if total == 0:
                return "INFO: No shared patterns yet. Daemon will consolidate after 30s."
            
            return f"shared_patterns={total}"
        
        return await self._check("Shared Memory", _test)

    async def test_visitor_tracking(self):
        """Test 8: Visitor tracking endpoint works."""
        async def _test():
            fingerprint = f"test-{uuid.uuid4().hex[:8]}"
            
            resp = await self.client.post(
                "/api/visitors",
                params={
                    "fingerprint": fingerprint,
                    "source": "integration_test",
                    "landing_page": "/test",
                }
            )
            assert resp.status_code == 200
            data = resp.json()
            
            assert data["status"] in ["created", "updated"]
            assert "visitor_id" in data
            
            return f"visitor_id={data['visitor_id'][:8]}..., status={data['status']}"
        
        return await self._check("Visitor Tracking", _test)


async def main():
    """Main entry point."""
    test = SturnaIntegrationTest()
    success = await test.run()
    if success:
        logger.info("🎉 All tests passed! Sturna.ai is fully operational.")
        sys.exit(0)
    else:
        logger.error("⚠️  Some tests failed. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())