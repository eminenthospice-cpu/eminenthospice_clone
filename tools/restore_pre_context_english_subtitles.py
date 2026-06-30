from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIVERABLES = ROOT / "deliverables" / "youtube-subtitles"
BACKUP = DELIVERABLES / "_pre-context-rewrite-backup"

manifest = json.loads((DELIVERABLES / "manifest.json").read_text(encoding="utf-8"))
for item in manifest:
    name = f"{item['youtube_id']}-{item['slug']}"
    source = BACKUP / f"{name}.en-subtitles.srt"
    target = DELIVERABLES / name / "en-subtitles.srt"
    if not source.exists():
        raise FileNotFoundError(source)
    shutil.copy2(source, target)
    print(f"restored {item['youtube_id']}")
