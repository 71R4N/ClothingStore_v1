import os
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.api.v1 import v1_router
from app.core.redis_client import redis_client
from app.core.middleware import CSRFMiddleware

app = FastAPI(title="CatVTON Shop", version="0.1.0")
app.add_middleware(CSRFMiddleware)
app.include_router(v1_router, prefix="/api/v1")
os.makedirs("static/tryon_results", exist_ok=True)
app.mount("/tryon_results", StaticFiles(directory="static/tryon_results"), name="tryon_results")

@app.on_event("startup")
async def startup():
    await redis_client.connect()

@app.get("/health")
async def health():
    return {"status": "ok"}
