from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Compliance routers
from app.api.routes.human_reviews import router as human_reviews_router
from app.api.routes.evidence import router as evidence_router
from app.api.routes.ai_inventory import router as ai_inventory_router

# Observability
from app.observability.tracing import tracing

app = FastAPI(title="Sturna.ai - Galaxy Enterprise v2", description="100+ Domain Compliance AI Orchestration Platform")

app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

# Include compliance routers
app.include_router(human_reviews_router)
app.include_router(evidence_router)
app.include_router(ai_inventory_router)

# Instrument tracing
tracing.instrument_fastapi(app)


@app.get('/')
def root():
    return {'message': '✅ Sturna.ai Galaxy Enterprise v2 LIVE - 100+ Domains, Biomimetic Agents, PQC + Nova zk-SNARKs'}

@app.get('/health')
def health():
    return {'status': 'healthy', 'domains': 112, 'version': 'enterprise-v2'}

print('Sturna.ai full enterprise stack loaded')