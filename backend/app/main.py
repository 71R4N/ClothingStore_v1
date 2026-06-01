import os
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.api.v1 import v1_router
from app.core.middleware import setup_cors

app = FastAPI(title="CatVTON Shop", version="0.1.0")
setup_cors(app)
app.include_router(v1_router, prefix="/api/v1")
os.makedirs("static/tryon_results", exist_ok=True)
app.mount("/tryon_results", StaticFiles(directory="static/tryon_results"), name="tryon_results")

@app.get("/health")
async def health():
    return {"status": "ok"}
