from fastapi import APIRouter, UploadFile, File
from insightify.transcriber import Transcriber
from insightify.insights import InsightEngine
from app.schemas import TranscriptionResponse, InsightResponse

router = APIRouter()

transcriber = Transcriber(model_size="tiny")
engine = InsightEngine()


@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    file_path = f"data/uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = transcriber.transcribe(file_path)

    insights = engine.generate(result["full_text"])

    return {
        "transcription": result,
        "insights": insights
    }
