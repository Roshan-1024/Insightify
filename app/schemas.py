from pydantic import BaseModel
from typing import List, Dict, Any


class Segment(BaseModel):
    start: float
    end: float
    text: str


class TranscriptionResponse(BaseModel):
    full_text: str
    segments: List[Segment]


class InsightResponse(BaseModel):
    summary: str
    key_points: List[str]
    topics: List[str]
