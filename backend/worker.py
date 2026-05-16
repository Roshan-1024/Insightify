import redis
from celery import Celery
from insightify.insights import InsightEngine
from insightify.transcriber import Transcriber
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
import json
import os


redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
celery_app = Celery(
    "insightify_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

print("Loading AI model into RAM/VRAM")
transcriber = Transcriber(model_size="tiny")
engine = InsightEngine()
print("Models loaded and worker is ready")


def update_data(job_id, data):
    current_data = json.loads(redis_client.get(job_id) or "{}")
    current_data.update(data)
    redis_client.set(job_id, json.dumps(current_data))


@celery_app.task(name="process_video")
def process_video(job_id: str, file_path: str):
    try:
        # Generate Transcription with timestamps
        print(f"Transcribing {job_id}")
        update_data(job_id, {
            "status": "transcribing",
        })
        transcription = transcriber.transcribe(file_path)
        update_data(job_id, {
            "status": "analyzing",
            "transcription": transcription
        })

        # Generate insights using LLM
        print(f"Generating insights {job_id}")
        insights = engine.generate(transcription["full_text"])

        update_data(job_id, {
            "status": "completed",
            "insights": insights
        })

    except Exception as e:
        update_data(job_id, {
            "status": "failed",
            "error": str(e)
        })

    finally: # cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Uploaded file with id '{job_id}' cleaned.")
