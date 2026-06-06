import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1 import v1_router
from app.core.redis_client import redis_client
from app.core.middleware import CSRFMiddleware
from app.core.config import settings
from app.admin import setup_admin
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.connect()
    yield
    await redis_client.disconnect()


app = FastAPI(title="CatVTON Shop", version="0.1.0", lifespan=lifespan)

# Middleware для сессий (требуется для аутентификации SQLAdmin)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY
)

# CSRF Middleware (исключаем /admin из проверки)
# Примечание: нужно обновить CSRFMiddleware, чтобы он пропускал /admin
app.add_middleware(CSRFMiddleware)

# CORS
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-роутеры
app.include_router(v1_router, prefix="/api/v1")

# Статические файлы
app.mount("/images", StaticFiles(directory="static/images"), name="images")
os.makedirs("static/tryon_results", exist_ok=True)
app.mount("/tryon_results", StaticFiles(directory="static/tryon_results"), name="tryon_results")


# Инициализация админ-панели
setup_admin(app)


@app.on_event("startup")
async def startup():
    await redis_client.connect()


@app.get("/health")
async def health():
    return {"status": "ok"}