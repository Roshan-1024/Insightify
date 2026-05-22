import os
import json
from celery import Celery

from insightify.insights import InsightEngine
from insightify.transcriber import Transcriber
from backend.database import SessionLocal
from backend.models import VideoBase



REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379/0"
)
celery_app = Celery(
    "insightify_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

print("Loading AI model into RAM/VRAM")
transcriber = Transcriber(model_size="tiny")
engine = InsightEngine()
print("Models loaded and worker is ready")


@celery_app.task(name="process_video")
def process_video(job_id: str, file_path: str):
    db = SessionLocal()

    # Fetch the row created in analyze endpoint
    try:
        video = db.query(VideoBase).filter(VideoBase.id == job_id).first()
        if not video:
            print(f"Video {job_id} not found in database")
            return

        # Generate Transcription with timestamps
        print(f"Transcribing {job_id}")
        video.status = "processing"
        db.commit()

        transcription = transcriber.transcribe(file_path)

        video.transcript = json.dumps(transcription)
        video.status = "analyzing"
        db.commit()

        # Generate insights using LLM
        print(f"Generating insights {job_id}")
        insights = engine.generate(transcription["full_text"])

        # Check if insights generation silently failed
        if "error" in insights:
            raise Exception(f"Error generating insights: {insights['error']}")

        video.status = "completed"
        video.insights = insights
        db.commit()

    except Exception as e:
        db.rollback()
        video = db.query(VideoBase).filter(VideoBase.id == job_id).first()
        if video:
            video.status = "failed"
            video.error = str(e)
            db.commit()

        print(f"Worker failed on {job_id}: {str(e)}")

    finally: # cleanup
        db.close()
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Uploaded file with id '{job_id}' cleaned.")
