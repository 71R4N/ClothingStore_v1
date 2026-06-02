import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.api.v1 import v1_router
from app.core.redis_client import redis_client
from app.core.middleware import CSRFMiddleware
from app.core.config import settings
from contextlib import asynccontextmanager
from app.core.redis_client import redis_client
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()
    yield
    await redis_client.disconnect()

app = FastAPI(title="CatVTON Shop", version="0.1.0", lifespan=lifespan)
app.add_middleware(CSRFMiddleware)
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(v1_router, prefix="/api/v1")
app.mount("/images", StaticFiles(directory="static/images"), name="images")
os.makedirs("static/tryon_results", exist_ok=True)
app.mount("/tryon_results", StaticFiles(directory="static/tryon_results"), name="tryon_results")

@app.on_event("startup")
async def startup():
    await redis_client.connect()

@app.get("/health")
async def health():
    return {"status": "ok"}
