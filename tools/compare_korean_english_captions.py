from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = ROOT / "deliverables" / "youtube-subtitles"
CACHE = json.loads(
    (ROOT / "audit" / "youtube_translation_cache.json").read_text(encoding="utf-8")
)


def parse_srt(path: Path) -> list[dict[str, str | int]]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    entries = []
    for block in re.split(r"\n{2,}", text):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        entries.append(
            {
                "number": int(lines[0]),
                "timing": lines[1].strip(),
                "text": " ".join(line.strip() for line in lines[2:] if line.strip()),
            }
        )
    return entries


def main() -> None:
    manifest = json.loads(
        (DELIVERABLES / "manifest.json").read_text(encoding="utf-8")
    )
    results = []
    for item in manifest:
        folder = DELIVERABLES / f"{item['youtube_id']}-{item['slug']}"
        korean = parse_srt(folder / "ko-transcript.srt")
        english = parse_srt(folder / "en-subtitles.srt")
        if len(korean) != len(english):
            raise ValueError(
                f"{item['youtube_id']}: {len(korean)} Korean vs {len(english)} English"
            )

        changed = []
        for ko, en in zip(korean, english, strict=True):
            if ko["number"] != en["number"] or ko["timing"] != en["timing"]:
                raise ValueError(
                    f"{item['youtube_id']} cue alignment mismatch at {ko['number']}"
                )
            baseline = CACHE.get(str(ko["text"]), "")
            if baseline and baseline != en["text"]:
                changed.append(
                    {
                        "cue": ko["number"],
                        "timing": ko["timing"],
                        "korean": ko["text"],
                        "baseline_english": baseline,
                        "current_english": en["text"],
                    }
                )
        results.append(
            {
                "youtube_id": item["youtube_id"],
                "slug": item["slug"],
                "total_cues": len(korean),
                "changed_from_direct_translation": changed,
            }
        )

    output = DELIVERABLES / "korean-english-comparison.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)
    print(f"videos={len(results)}")
    print(f"cues={sum(item['total_cues'] for item in results)}")
    print(
        "changed="
        f"{sum(len(item['changed_from_direct_translation']) for item in results)}"
    )


if __name__ == "__main__":
    main()
