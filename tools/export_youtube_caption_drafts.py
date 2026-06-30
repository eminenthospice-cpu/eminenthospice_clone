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


SOURCE_DIR = ROOT / "audit" / "youtube_auto_captions"
OUT_DIR = ROOT / "deliverables" / "youtube-subtitles"
CACHE_PATH = ROOT / "audit" / "youtube_translation_cache.json"

VIDEOS = [
    ("42r5f9uf-0U", "polst"),
    ("K0bgtz2gV40", "hospice-core-services"),
    ("v9-onN7EsWo", "hospice-myths"),
    ("XeGjlf7fILA", "after-death-hospice"),
    ("SNGsCjicC8E", "after-death-non-hospice"),
    ("3mgBE6CaI4I", "end-of-life-timing"),
    ("edmwae3Iglk", "nebulizer"),
    ("Vq5rIpelzhk", "oxygen-concentrator"),
    ("9g98EDnOAUI", "suction-machine"),
    ("qWl3XdJ4rck", "hospice-aide-perspective"),
    ("jsPCywsMe5Y", "hospice-nurse-perspective"),
    ("xnI28GlZwZI", "american-hospice-nurse"),
    ("Rv1Cbnb4QDA", "emergency-medications"),
    ("2Ci1inVJrrc", "chaplain-perspective"),
]


def parse_srt(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    entries = []
    for block in re.split(r"\n{2,}", text):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        entries.append(
            {
                "timing": lines[1].strip(),
                "text": " ".join(line.strip() for line in lines[2:] if line.strip()),
            }
        )
    return entries


def write_srt(path: Path, entries: list[dict[str, str]], texts: list[str]) -> None:
    blocks = [
        f"{index}\n{entry['timing']}\n{text}"
        for index, (entry, text) in enumerate(zip(entries, texts, strict=True), start=1)
    ]
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def clean_english(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    replacements = {
        "Eminent Speech Care": "Eminent Hospice Care",
        "Eminent Hospice Care Care": "Eminent Hospice Care",
        "Hofis": "hospice",
        "Hospis": "hospice",
        "hospis": "hospice",
        "narcotic analgesic": "opioid pain medication",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def translate_chunk(
    texts: list[str],
    translator: GoogleTranslator,
) -> list[str]:
    if len(texts) == 1:
        return [clean_english(translator.translate(texts[0]))]
    parts = []
    for index, text in enumerate(texts):
        if index:
            parts.append(f"ZXQSEP{index:04}ZXQ")
        parts.append(text)
    translated = translator.translate("\n".join(parts))
    results = re.split(r"\s*ZXQSEP\d{4}ZXQ\s*", translated)
    if len(results) != len(texts):
        return [clean_english(translator.translate(text)) for text in texts]
    return [clean_english(result) for result in results]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = (
        json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if CACHE_PATH.exists()
        else {}
    )
    translator = GoogleTranslator(source="ko", target="en")
    manifest = []

    for video_id, slug in VIDEOS:
        source = SOURCE_DIR / f"{video_id}.ko.srt"
        if not source.exists():
            raise FileNotFoundError(source)
        entries = parse_srt(source)
        folder = OUT_DIR / f"{video_id}-{slug}"
        folder.mkdir(parents=True, exist_ok=True)

        korean = [entry["text"] for entry in entries]
        write_srt(folder / "ko-transcript.srt", entries, korean)
        (folder / "ko-transcript.txt").write_text(
            "\n".join(
                f"[{entry['timing']}] {entry['text']}" for entry in entries
            )
            + "\n",
            encoding="utf-8",
        )

        english = [""] * len(korean)
        print(f"{video_id} {slug}: {len(entries)} captions", flush=True)
        pending: list[tuple[int, str]] = []
        for index, text in enumerate(korean):
            if text in cache:
                english[index] = cache[text]
                continue
            pending.append((index, text))

        cursor = 0
        while cursor < len(pending):
            chunk = []
            char_count = 0
            while cursor + len(chunk) < len(pending) and len(chunk) < 25:
                candidate = pending[cursor + len(chunk)][1]
                if chunk and char_count + len(candidate) > 3000:
                    break
                chunk.append(pending[cursor + len(chunk)])
                char_count += len(candidate)
            chunk_texts = [text for _, text in chunk]

            for attempt in range(5):
                try:
                    translated_texts = translate_chunk(chunk_texts, translator)
                    if len(translated_texts) != len(chunk):
                        raise ValueError("translation count mismatch")
                    for (target_index, korean_text), translated in zip(
                        chunk, translated_texts, strict=True
                    ):
                        if not translated:
                            raise ValueError("empty translation")
                        cache[korean_text] = translated
                        english[target_index] = translated
                    break
                except Exception as exc:
                    if attempt == 4:
                        raise RuntimeError(
                            f"{video_id}: translation failed near caption {chunk[0][0] + 1}"
                        ) from exc
                    time.sleep(2 ** attempt)
            cursor += len(chunk)
            CACHE_PATH.write_text(
                json.dumps(cache, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"  {cursor}/{len(pending)} new captions", flush=True)

        write_srt(folder / "en-subtitles.srt", entries, english)
        CACHE_PATH.write_text(
            json.dumps(cache, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        manifest.append(
            {
                "youtube_id": video_id,
                "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                "slug": slug,
                "captions": len(entries),
                "korean_transcript": str((folder / "ko-transcript.txt").relative_to(ROOT)),
                "korean_srt": str((folder / "ko-transcript.srt").relative_to(ROOT)),
                "english_srt": str((folder / "en-subtitles.srt").relative_to(ROOT)),
                "review_status": "Machine-generated draft; bilingual clinical review required",
            }
        )

    (OUT_DIR / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / "README.md").write_text(
        "# Korean transcripts and English subtitle drafts\n\n"
        "Each video folder contains:\n\n"
        "- `ko-transcript.txt`: time-coded Korean transcript\n"
        "- `ko-transcript.srt`: Korean subtitle track\n"
        "- `en-subtitles.srt`: English translation track\n\n"
        "The Korean timing/text starts from YouTube's Korean caption track. The "
        "English text is a new translation from that Korean track, not the old "
        "website subtitle files.\n\n"
        "**Clinical review required:** speech recognition and machine translation "
        "can misstate names, medications, dosages, symptoms, and instructions. A "
        "bilingual hospice clinician must review every file before publication.\n",
        encoding="utf-8",
    )
    print(f"Complete: {len(manifest)} video sets", flush=True)


if __name__ == "__main__":
    main()
