# Replace: app/api/ingestion.py
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import uuid
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])

STORAGE_RAW = Path("storage/raw")
STORAGE_RAW.mkdir(parents=True, exist_ok=True)

class IngestionResponse(BaseModel):
    ingestion_id: str
    source: str
    media_type: str
    status: str

@router.post("/upload", response_model=IngestionResponse)
async def upload_field_update(
    source: str = Form("web_upload"),
    media_type: str = Form("text"),
    raw_text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Receives raw field updates (voice, text, photo) and stores them."""
    ingestion_id = f"ING-{uuid.uuid4().hex[:8].upper()}"
    
    if file:
        file_path = STORAGE_RAW / f"{ingestion_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    return {
        "ingestion_id": ingestion_id,
        "source": source,
        "media_type": media_type,
        "status": "received"
    }