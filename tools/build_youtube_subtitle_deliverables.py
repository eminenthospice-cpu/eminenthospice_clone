from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCAL_PACKAGES = ROOT / "audit" / "local_python_packages"
if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

from deep_translator import GoogleTranslator  # noqa: E402


OUT_DIR = ROOT / "deliverables" / "youtube-subtitles"
OLD_DIR = ROOT / "audit" / "video_caption_remediation"
NEW_DIR = ROOT / "audit" / "youtube_transcripts"
CACHE_PATH = ROOT / "audit" / "youtube_translation_cache.json"

VIDEOS = [
    ("42r5f9uf-0U", "polst", OLD_DIR / "polst-korean-english-subtitles.ko.transcript.json"),
    ("K0bgtz2gV40", "hospice-core-services", NEW_DIR / "hospice-core-services.ko.json"),
    ("v9-onN7EsWo", "hospice-myths", OLD_DIR / "hospice-myths-korean-english-subtitles.ko.transcript.json"),
    ("XeGjlf7fILA", "after-death-hospice", OLD_DIR / "after-death-hospice-korean-english-subtitles.ko.transcript.json"),
    (
        "SNGsCjicC8E",
        "after-death-non-hospice",
        OLD_DIR / "after-death-non-hospice-polst-korean-english-subtitles.ko.transcript.json",
    ),
    ("3mgBE6CaI4I", "end-of-life-timing", OLD_DIR / "end-of-life-timing-korean-english-subtitles.ko.transcript.json"),
    ("edmwae3Iglk", "nebulizer", NEW_DIR / "nebulizer.ko.json"),
    ("Vq5rIpelzhk", "oxygen-concentrator", NEW_DIR / "oxygen-concentrator.ko.json"),
    ("9g98EDnOAUI", "suction-machine", NEW_DIR / "suction-machine.ko.json"),
    (
        "qWl3XdJ4rck",
        "hospice-aide-perspective",
        OLD_DIR / "hospice-team-interview-younghee-kim-korean-english-subtitles.ko.transcript.json",
    ),
    (
        "jsPCywsMe5Y",
        "hospice-nurse-perspective",
        OLD_DIR / "hospice-nurse-interview-janice-korean-english-subtitles.ko.transcript.json",
    ),
    ("xnI28GlZwZI", "american-hospice-nurse", NEW_DIR / "american-hospice-nurse.ko.json"),
    ("Rv1Cbnb4QDA", "emergency-medications", NEW_DIR / "emergency-medications.ko.json"),
    (
        "2Ci1inVJrrc",
        "chaplain-perspective",
        OLD_DIR / "hospice-social-work-bereavement-interview-peter-park-korean-english-subtitles.ko.transcript.json",
    ),
]


def srt_time(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def normalize_english(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    replacements = {
        "Hofis": "hospice",
        "Hospis": "hospice",
        "POLST form": "POLST",
        "terminal period": "end of life",
        "narcotic painkiller": "opioid pain medication",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def translate_segments(segments: list[dict], cache: dict[str, str]) -> list[str]:
    translator = GoogleTranslator(source="ko", target="en")
    translated: list[str] = []
    for index, segment in enumerate(segments, start=1):
        korean = segment["text"].strip()
        if korean in cache:
            translated.append(cache[korean])
            continue
        for attempt in range(5):
            try:
                english = normalize_english(translator.translate(korean))
                if not english:
                    raise ValueError("empty translation")
                cache[korean] = english
                translated.append(english)
                if index % 25 == 0:
                    CACHE_PATH.write_text(
                        json.dumps(cache, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    print(f"  translated {index}/{len(segments)}", flush=True)
                break
            except Exception as exc:
                if attempt == 4:
                    raise RuntimeError(f"Translation failed at segment {index}: {korean}") from exc
                time.sleep(2 ** attempt)
    return translated


def write_srt(path: Path, segments: list[dict], texts: list[str]) -> None:
    blocks = []
    for index, (segment, text) in enumerate(zip(segments, texts, strict=True), start=1):
        blocks.append(
            f"{index}\n{srt_time(float(segment['start']))} --> "
            f"{srt_time(float(segment['end']))}\n{text}"
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def main() -> None:
    missing = [str(path) for _, _, path in VIDEOS if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing transcript inputs:\n" + "\n".join(missing))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = (
        json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if CACHE_PATH.exists()
        else {}
    )

    manifest = []
    for video_id, slug, transcript_path in VIDEOS:
        print(f"{video_id} {slug}", flush=True)
        data = json.loads(transcript_path.read_text(encoding="utf-8"))
        segments = [
            segment
            for segment in data["segments"]
            if segment.get("text", "").strip()
        ]
        folder = OUT_DIR / f"{video_id}-{slug}"
        folder.mkdir(parents=True, exist_ok=True)

        korean_texts = [segment["text"].strip() for segment in segments]
        write_srt(folder / "ko-transcript.srt", segments, korean_texts)
        (folder / "ko-transcript.txt").write_text(
            "\n".join(
                f"[{srt_time(float(segment['start']))} --> "
                f"{srt_time(float(segment['end']))}] {segment['text'].strip()}"
                for segment in segments
            )
            + "\n",
            encoding="utf-8",
        )

        english_texts = translate_segments(segments, cache)
        write_srt(folder / "en-subtitles.srt", segments, english_texts)
        manifest.append(
            {
                "youtube_id": video_id,
                "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                "slug": slug,
                "segment_count": len(segments),
                "korean_transcript": str((folder / "ko-transcript.txt").relative_to(ROOT)),
                "korean_srt": str((folder / "ko-transcript.srt").relative_to(ROOT)),
                "english_srt": str((folder / "en-subtitles.srt").relative_to(ROOT)),
                "review_status": "Machine draft - requires bilingual clinical review",
            }
        )
        CACHE_PATH.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "README.md").write_text(
        "# YouTube subtitle deliverables\n\n"
        "Each folder contains a time-coded Korean transcript (`.txt` and `.srt`) "
        "and an English `.srt` translation.\n\n"
        "**Important:** These files are machine-generated drafts. Because the "
        "videos contain hospice and medication information, a bilingual clinician "
        "must review the Korean transcript and English translation before publication.\n",
        encoding="utf-8",
    )
    print(f"Created {len(manifest)} video deliverable sets in {OUT_DIR}", flush=True)


if __name__ == "__main__":
    main()
