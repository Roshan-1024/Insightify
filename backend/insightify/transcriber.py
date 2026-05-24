import whisper
import os


class Transcriber:
    def __init__(self, model_size: str = "tiny", model_dir: str = "./models"):
        self.model_size = model_size

        os.makedirs(model_dir, exist_ok=True)

        print(f"[INFO] Loading Whisper model: {model_size}")

        self.model = whisper.load_model(
            model_size,
            download_root=model_dir
        )

        print("[INFO] Model loaded successfully")

    def transcribe(self, video_path: str):
        print(f"[INFO] Transcribing: {video_path}")

        result = self.model.transcribe(video_path)

        print("[INFO] Transcription done")

        segments = [
            {
                "start": round(s["start"], 2),
                "end": round(s["end"], 2),
                "text": s["text"].strip()
            }
            for s in result.get("segments", [])
        ]

        return {
            "language": result.get("language"),
            "full_text": result.get("text", "").strip(),
            "segments": segments
        }
