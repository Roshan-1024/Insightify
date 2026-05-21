import os
import mimetypes
import json
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import VideoBase
from backend.worker import process_video



router = APIRouter()

ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/x-matroska",  # .mkv
    "video/quicktime",   # .mov
    "audio/mpeg",        # .mp3
    "audio/wav",
    "audio/x-wav"
}

@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Check uploaded file type before downloading
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415, # Unsupported Media Type
            detail=f"Invalid file type {file.content_type}. Expected MP4, MKV, MOV, MP3 or WAV"
        )

    db_video = VideoBase(
        filename=file.filename,
        status="processing"
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)

    job_id = str(db_video.id)
    # some OS don't have complete MIME database; default to .bin
    extension = mimetypes.guess_extension(file.content_type) or ".bin"
    file_path = f"data/uploads/{job_id}{extension}"

    os.makedirs("data/uploads", exist_ok=True)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Send task to Celery worker queue
    process_video.delay(job_id, file_path)

    return {"job_id": job_id, "status": "accepted"}

@router.get("/status/{job_id}")
async def get_status(job_id: str, db: Session = Depends(get_db)):
    video = db.query(VideoBase).filter(VideoBase.id == job_id).first()

    if not video:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "status": video.status,
        "filename": video.filename,
        "transcription": json.loads(video.transcript) if video.transcript else None,
        "insights": video.insights,
        "error": video.error
    }

