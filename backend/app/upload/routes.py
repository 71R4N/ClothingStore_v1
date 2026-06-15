import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only images are allowed")

    os.makedirs("/app/static/uploads", exist_ok=True)
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4()}.{file_ext}"
    filepath = f"/app/static/uploads/{filename}"

    with open(filepath, "wb") as f:
        f.write(await file.read())

    return {"url": f"/static/uploads/{filename}"}
