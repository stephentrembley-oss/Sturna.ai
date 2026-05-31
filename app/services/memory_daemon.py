"""Memory Daemon — Background memory consolidation service.

Runs:
•  Every 30 seconds: Extract patterns from recent memories
•  Daily 2am-5am UTC: Full consolidation pass
•  Weekly: Shared memory graph optimization
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

import structlog

from app.services.memory import MemoryService
from app.models.base import async_session

logger = structlog.get_logger("memory_daemon")


class MemoryDaemon:
    """Background service for memory maintenance."""

    def __init__(self):
        self.running = False
        self.last_consolidation: Optional[datetime] = None

    async def start(self):
        """Start the memory daemon loop."""
        self.running = True
        logger.info("memory_daemon_started")
        
        while self.running:
            try:
                # Quick extraction pass (every 30s)
                await self._extraction_pass()
                
                # Full consolidation (daily 2am-5am window)
                now = datetime.utcnow()
                if 2 <= now.hour < 5:
                    if not self.last_consolidation or (now - self.last_consolidation).days >= 1:
                        await self._consolidation_pass()
                        self.last_consolidation = now
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error("memory_daemon_error", error=str(e))
                await asyncio.sleep(60)

    async def _extraction_pass(self):
        """Quick pattern extraction from recent memories."""
        async with async_session() as db:
            service = MemoryService(db)
            
            # Run decay for all agents
            await service.run_decay()
            
            logger.debug("extraction_pass_complete")

    async def _consolidation_pass(self):
        """Full consolidation pass — promote patterns to shared memory."""
        async with async_session() as db:
            service = MemoryService(db)
            
            # Consolidate by category
            for category in ["intent_pattern", "anti_pattern", "coalition_insight"]:
                result = await service.consolidate_shared_memory(
                    category=category,
                    min_confidence=0.7,
                    min_frequency=3,
                )
                logger.info(
                    "consolidation_category",
                    category=category,
                    patterns=result["patterns_consolidated"],
                )
            
            logger.info("full_consolidation_complete")

    def stop(self):
        """Stop the daemon."""
        self.running = False
        logger.info("memory_daemon_stopped")


# Singleton
_daemon = None

def get_memory_daemon() -> MemoryDaemon:
    global _daemon
    if _daemon is None:
        _daemon = MemoryDaemon()
    return _daemon