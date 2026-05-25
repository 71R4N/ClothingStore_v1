from fastapi import FastAPI
from app.api.v1 import v1_router
from app.core.middleware import setup_cors

app = FastAPI(title="CatVTON Shop", version="0.1.0")
setup_cors(app)
app.include_router(v1_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}
