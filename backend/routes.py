from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from backend.worker import process_video
import uuid
import mimetypes
import redis
import json
import shutil


router = APIRouter()
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/x-matroska",  # .mkv
    "video/quicktime",   # .mov
    "audio/mpeg",        # .mp3
    "audio/wav",
    "audio/x-wav"
}

@router.post("/analyze")
async def analyze_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    # Check uploaded file type before downloading
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415, # Unsupported Media Type
            detail=f"Invalid file type {file.content_type}. Expected MP4, MKV, MOV, MP3 or WAV"
        )

    job_id = str(uuid.uuid4())
    # some OS don't have complete MIME database; default to .bin
    extension = mimetypes.guess_extension(file.content_type) or ".bin"
    file_path = f"data/uploads/{job_id}{extension}"

    # write locally (for now...)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize job state
    initial_state = {
        "status": "processing",
        "original_filename": file.filename,
        "transcription": None,
        "insights": None
    }

    redis_client.set(job_id, json.dumps(initial_state))

    # Send task to Celery worker queue
    process_video.delay(job_id, file_path)

    return {"job_id": job_id, "status": "accepted"}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    data = redis_client.get(job_id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return json.loads(data)

