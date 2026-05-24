import os
import time
import json
from dotenv import load_dotenv
import google.generativeai as genai
import typing_extensions as typing

load_dotenv()

class VideoAnalysis(typing.TypedDict):
    summary: str
    key_points: list[str]
    topics: list[str]

class InsightEngine:
    def __init__(self, model_name="gemini-2.5-flash-lite"):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction="You are a video analysis system."
        )

    def generate(self, transcript: str):
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=VideoAnalysis,
            temperature=0.2
        )

        try:
            response = self.model.generate_content(
                f"Transcript:\n{transcript}",
                generation_config=generation_config
            )

            time.sleep(4)

            return json.loads(response.text)

        except Exception as e:
            return {
                "raw_output": None,
                "error": f"API Error: {str(e)}"
            }
