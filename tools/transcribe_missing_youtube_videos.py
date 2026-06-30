from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_PACKAGES = ROOT / "audit" / "local_python_packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

from faster_whisper import WhisperModel  # noqa: E402


OUT_DIR = ROOT / "audit" / "youtube_transcripts"
MODEL_ROOT = (
    Path.home()
    / ".cache"
    / "huggingface"
    / "hub"
    / "models--Systran--faster-whisper-small"
    / "snapshots"
)

SOURCES = {
    "hospice-core-services": Path.home() / "Downloads" / "videoplayback (1).mp4",
    "oxygen-concentrator": Path.home() / "Downloads" / "YTDown_YouTube_Media_Vq5rIpelzhk_001_1080p.mp4",
    "nebulizer": Path.home() / "Downloads" / "YTDown_YouTube_Media_edmwae3Iglk_001_1080p.mp4",
    "suction-machine": Path.home() / "Downloads" / "YTDown_YouTube_Media_9g98EDnOAUI_001_1080p.mp4",
    "emergency-medications": Path.home() / "Downloads" / "YTDown_YouTube_Media_Rv1Cbnb4QDA_001_1080p.mp4",
    "american-hospice-nurse": ROOT / "audit" / "source_videos" / "xnI28GlZwZI.m4a",
}


def find_model() -> Path:
    snapshots = sorted(MODEL_ROOT.glob("*"))
    if not snapshots:
        raise FileNotFoundError(f"No cached model found under {MODEL_ROOT}")
    return snapshots[-1]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    model_path = find_model()
    model = WhisperModel(str(model_path), device="cpu", compute_type="int8")

    for slug, source in SOURCES.items():
        output = OUT_DIR / f"{slug}.ko.json"
        if output.exists():
            print(f"{slug}: already transcribed", flush=True)
            continue
        if not source.exists():
            raise FileNotFoundError(source)

        print(f"{slug}: transcribing {source.name}", flush=True)
        segments_iter, info = model.transcribe(
            str(source),
            language="ko",
            task="transcribe",
            word_timestamps=True,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 350},
            beam_size=5,
            best_of=5,
            temperature=0,
            condition_on_previous_text=True,
        )
        segments = [
            {
                "id": segment.id,
                "start": round(float(segment.start), 3),
                "end": round(float(segment.end), 3),
                "text": segment.text.strip(),
            }
            for segment in segments_iter
            if segment.text.strip()
        ]
        output.write_text(
            json.dumps(
                {
                    "source": str(source),
                    "language": info.language,
                    "language_probability": info.language_probability,
                    "duration": info.duration,
                    "segments": segments,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"{slug}: {len(segments)} segments", flush=True)


if __name__ == "__main__":
    main()
