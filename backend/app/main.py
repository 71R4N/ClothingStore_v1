from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.router import v1_router

app = FastAPI(
    title="Clothing Store API",
    description="Web-приложение для магазина одежды с виртуальной примеркой",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
