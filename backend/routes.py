from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from insightify.transcriber import Transcriber
from insightify.insights import InsightEngine
from backend.schemas import TranscriptionResponse
import uuid
import mimetypes
import os

router = APIRouter()

transcriber = Transcriber(model_size="tiny")
engine = InsightEngine()

# Volatile in-memory storage. Later Redis will be used.
jobs = {}

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
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Initialize job state
    jobs[job_id] = {
        "status": "processing",
        "original_filename": file.filename,
        "result": None,
        "insights": None
    }

    background_tasks.add_task(run_inference, job_id, file_path)

    return {"job_id": job_id, "status": "accepted"}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

def run_inference(job_id: str, file_path: str):
    try:
        # Generate Transcription with timestamps
        result = transcriber.transcribe(file_path)

        # Generate insights using LLM
        insights = engine.generate(result["full_text"])

        jobs[job_id].update({
            "status": "completed",
            "result": result,
            "insights": insights
        })

    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}

    finally: # cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            print("Uploaded file with id '{job_id}' cleaned.")
