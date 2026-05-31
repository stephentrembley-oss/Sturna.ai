"""Sturna.ai — FastAPI Application Entry Point (Phase 2 + API Wired).
Run: uvicorn main:app --reload
"""
import os
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import structlog

from app.models.base import engine, Base
from app.api import health, agents, memories, auctions, visitors, demos, intents
from app.core.intent_engine import get_intent_engine
from app.core.galaxy_manager import get_galaxy_manager
from app.core.dag_scheduler import get_dag_scheduler
from app.core.compliance import get_compliance_classifier
from app.core.grounding import get_grounding_gate

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("sturna")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("sturna_startup", message="Sturna.ai Phase 2+3 starting up", version="2.2.0")

    # === Run database migrations on startup (recommended for Render) ===
    if os.environ.get("RUN_MIGRATIONS", "false").lower() == "true":
        try:
            import subprocess
            logger.info("running_migrations", status="starting")
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            if result.returncode == 0:
                logger.info("migrations_completed", status="success")
            else:
                logger.warning("migrations_failed", stderr=result.stderr)
        except Exception as e:
            logger.error("migration_error", error=str(e))

    # Wire dependency injection
    intent_engine = get_intent_engine()
    galaxy_manager = get_galaxy_manager()
    dag_scheduler = get_dag_scheduler()
    compliance_classifier = get_compliance_classifier()
    grounding_gate = get_grounding_gate()

    intent_engine.set_galaxy_manager(galaxy_manager)
    intent_engine.set_dag_scheduler(dag_scheduler)
    intent_engine.set_grounding_gate(grounding_gate)

    # Start memory daemon in background
    from app.services.memory_daemon import get_memory_daemon
    memory_daemon = get_memory_daemon()

    daemon_task = asyncio.create_task(memory_daemon.start())
    logger.info("memory_daemon_started", status="background_task_created")

    logger.info(
        "dependencies_wired",
        intent_engine="ok",
        galaxy_manager="ok",
        dag_scheduler="ok",
        compliance="ok",
        grounding="ok",
        memory_daemon="ok",
    )

    # Create tables if they don't exist (safe even if some already exist)
    if os.environ.get("AUTO_CREATE_TABLES", "false").lower() == "true":
        async with engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))
        logger.info("sturna_db_init", message="Database tables auto-created (checkfirst=True)")

    yield

    # Shutdown
    memory_daemon.stop()
    daemon_task.cancel()
    try:
        await daemon_task
    except asyncio.CancelledError:
        pass

    logger.info("sturna_shutdown", message="Sturna.ai shutting down")
    await engine.dispose()


app = FastAPI(
    title="Sturna.ai",
    description="Compliance Intelligence, Verified by Design. Multi-agent orchestration with cryptographic proof.",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# === Serve Static Files from public/ ===
app.mount("/public", StaticFiles(directory="public"), name="public")


# === Middleware ===
# CORS - include Render frontend + localhost for development
origins = [
    "https://sturna.ai",
    "https://octomind-9fce.polsia.app",
    "https://sturna-ai-s862.onrender.com",  # Current Render deployment
    "http://localhost:3000",
    "http://localhost:8000",
]

# Allow any Render preview URLs (safe for pre-production)
if os.environ.get("RENDER_EXTERNAL_URL"):
    origins.append(os.environ["RENDER_EXTERNAL_URL"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# === Global Exception Handler ===
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. The incident has been logged.",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


# === Request ID Injection ===
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid
    request.state.request_id = str(uuid.uuid4())[:8]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response


# === Clean Demo Route ===
@app.get("/demo", include_in_schema=False)
async def demo_page():
    return FileResponse("public/demo.html")


# === Router Mounting ===
app.include_router(health.router, tags=["Health"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(memories.router, prefix="/api/memory", tags=["Memory"])
app.include_router(auctions.router, prefix="/api/auctions", tags=["Auctions"])
app.include_router(visitors.router, prefix="/api/visitors", tags=["Visitors"])
app.include_router(demos.router, prefix="/api/demos", tags=["Demos"])
app.include_router(intents.router, prefix="/api/intents", tags=["Intents"])


# === Root Endpoint ===
@app.get("/")
async def root():
    return {
        "service": "Sturna.ai",
        "version": "2.2.0",
        "tagline": "Compliance Intelligence, Verified by Design",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "features": [
            "5-stage-intent-pipeline",
            "coalition-market-auction",
            "triple-gate-verification",
        ],
    }


# === Health Endpoints ===
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "sturna", "phase": 2}


@app.get("/ready", tags=["Health"])
async def readiness_check():
    try:
        engine = get_intent_engine()
        ready = (
            engine.galaxy_manager is not None and
            engine.dag_scheduler is not None and
            engine.grounding_gate is not None
        )
        return {
            "status": "ready" if ready else "initializing",
            "checks": {
                "intent_engine": "ok",
                "galaxy_manager": "ok" if engine.galaxy_manager else "missing",
                "dag_scheduler": "ok" if engine.dag_scheduler else "missing",
                "grounding_gate": "ok" if engine.grounding_gate else "missing",
            }
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}