import json
from insightify.transcriber import Transcriber
from insightify.insights import InsightEngine


def main():
    video_path = "data/uploads/video.mp4"

    print("[1] Loading transcriber...")
    t = Transcriber(model_size="tiny")

    print("[2] Transcribing video...")
    result = t.transcribe(video_path)

    full_text = result["full_text"]
    segments = result["segments"]

    print("\n===== TRANSCRIPT PREVIEW =====\n")
    print(full_text)
    print("\nFirst 3 segments:")
    print(segments)

    print("\n[3] Generating insights...")
    engine = InsightEngine()

    output = engine.generate(full_text)

    print("\n===== INSIGHTS =====\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
