from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = ROOT / "deliverables" / "youtube-subtitles"
OUTPUT = DELIVERABLES / "ALL-14-ENGLISH-TRANSCRIPTS.txt"


def parse_srt(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    entries = []
    for block in re.split(r"\n{2,}", text):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        entries.append(
            (
                int(lines[0]),
                " ".join(line.strip() for line in lines[2:] if line.strip()),
            )
        )
    return entries


def main() -> None:
    manifest = json.loads(
        (DELIVERABLES / "manifest.json").read_text(encoding="utf-8")
    )
    sections = [
        "ALL 14 ENGLISH VIDEO TRANSCRIPTS",
        "",
        "How to report a correction:",
        'Video ID + line number + corrected English text',
        'Example: K0bgtz2gV40, line 23 → "corrected text"',
        "",
        "The line numbers match the cue numbers in the corresponding English SRT files.",
    ]

    for video_number, item in enumerate(manifest, start=1):
        folder = DELIVERABLES / f"{item['youtube_id']}-{item['slug']}"
        entries = parse_srt(folder / "en-subtitles.srt")
        sections.extend(
            [
                "",
                "=" * 80,
                f"VIDEO {video_number:02}/14",
                f"Video ID: {item['youtube_id']}",
                f"Topic: {item['slug']}",
                f"URL: {item['youtube_url']}",
                "=" * 80,
                "",
            ]
        )
        sections.extend(f"[{number:04}] {text}" for number, text in entries)

    OUTPUT.write_text("\n".join(sections) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
