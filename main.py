import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

# Compliance routers
from app.api.routes.human_reviews import router as human_reviews_router
from app.api.routes.evidence import router as evidence_router
from app.api.routes.ai_inventory import router as ai_inventory_router
from app.api.routes.explainability import router as explainability_router

# P0 Sprint routers
from app.api.routes.lead_gen import router as lead_gen_router
from app.api.routes.pilot_onboarding import router as pilot_onboarding_router
from app.api.routes.trust_shields import router as trust_shields_router
from app.api.routes.health_expanded import router as health_expanded_router

# Observability
from app.observability.tracing import tracing

app = FastAPI(title="Sturna.ai - Galaxy Enterprise v2", description="100+ Domain Compliance AI Orchestration Platform")

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

# Serve frontend files
static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include all routers
app.include_router(human_reviews_router)
app.include_router(evidence_router)
app.include_router(ai_inventory_router)
app.include_router(explainability_router)
app.include_router(lead_gen_router)
app.include_router(pilot_onboarding_router)
app.include_router(trust_shields_router)
app.include_router(health_expanded_router)

# Instrument tracing
tracing.instrument_fastapi(app)


# Create tables on startup
@app.on_event("startup")
def create_tables():
    from app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    print("[Startup] Database tables created/verified")


# Frontend pages
@app.get("/pilot", response_class=FileResponse)
async def pilot_page():
    return FileResponse(os.path.join(static_dir, "pilot_dashboard.html"))


@app.get("/trust", response_class=FileResponse)
async def trust_page():
    return FileResponse(os.path.join(static_dir, "trust_page.html"))


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/pilot")


@app.get('/health')
def health():
    return {'status': 'healthy', 'version': 'enterprise-v2'}

print('Sturna.ai full enterprise stack loaded')