from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sturna.ai", description="Compliance Intelligence Platform")

@app.get("/")
def root():
    return {"message": "✅ Sturna.ai is now live on Render!", "status": "healthy"}

@app.get("/health")
def health():
    return {"status": "ok"}
