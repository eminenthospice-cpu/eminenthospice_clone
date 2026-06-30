from __future__ import annotations

import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "audit" / "local_python_packages"
sys.path.insert(0, str(PACKAGES))
from deep_translator import GoogleTranslator  # noqa: E402

DELIVERABLES = ROOT / "deliverables" / "youtube-subtitles"
BACKUP = DELIVERABLES / "_pre-context-rewrite-backup"
CACHE_PATH = ROOT / "audit" / "context_translation_cache.json"

NOISE = {"ah", "ahhh", "ugh", "hahaha", "222", "4", "yes"}


def parse_time(value: str) -> float:
    h, m, rest = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def parse_srt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    rows = []
    for block in re.split(r"\n{2,}", text):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        start, end = [part.strip() for part in lines[1].split("-->")]
        rows.append(
            {
                "start": start,
                "end": end,
                "start_s": parse_time(start),
                "end_s": parse_time(end),
                "text": " ".join(lines[2:]).strip(),
            }
        )
    return rows


def group_rows(rows: list[dict]) -> list[dict]:
    groups = []
    current = None
    for row in rows:
        text = row["text"].strip()
        normalized = re.sub(r"[^A-Za-z가-힣]+", "", text).lower()
        if text == "[Music]" or normalized in NOISE or len(normalized) <= 1:
            if current:
                groups.append(current)
                current = None
            if text == "[Music]":
                groups.append({**row, "text": "[Music]"})
            continue
        if current is None:
            current = {**row}
            continue
        combined_length = len(current["text"]) + len(text)
        combined_duration = row["end_s"] - current["start_s"]
        if combined_length > 105 or combined_duration > 10:
            groups.append(current)
            current = {**row}
        else:
            current["end"] = row["end"]
            current["end_s"] = row["end_s"]
            current["text"] += " " + text
    if current:
        groups.append(current)
    return groups


def clean(text: str) -> str:
    replacements = {
        "Eminent Speech Care": "Eminent Hospice Care",
        "Eminent Peace Care": "Eminent Hospice Care",
        "Hostess": "Hospice",
        "hostess": "hospice",
        "Spieth": "hospice",
        "Folst": "POLST",
        "Holst": "POLST",
        "Poles": "POLST",
        "Line One": "911",
        "cardiopulmonary aquatic therapy": "cardiopulmonary resuscitation",
        "County Corona": "County Coroner",
        "Kaoni Corona": "County Coroner",
    }
    text = re.sub(r"\s+", " ", text).strip()
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\brace\b", "end of life", text, flags=re.I)
    text = re.sub(r"\brain\b", "pain", text, flags=re.I)
    if text and text[-1] not in ".?!]":
        text += "."
    if text:
        text = text[0].upper() + text[1:]
    return text


def translate(text: str, translator, cache: dict) -> str:
    if text == "[Music]":
        return text
    if text in cache:
        return cache[text]
    for attempt in range(5):
        try:
            result = clean(translator.translate(text))
            cache[text] = result
            return result
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def translate_all(groups: list[dict], translator, cache: dict) -> list[str]:
    output = [""] * len(groups)
    pending = []
    for index, group in enumerate(groups):
        text = group["text"]
        if text == "[Music]":
            output[index] = text
        elif text in cache:
            output[index] = cache[text]
        else:
            pending.append((index, text))
    for offset in range(0, len(pending), 20):
        batch = pending[offset : offset + 20]
        joined = "\n".join(
            (f"ZXQSEP{i:04}ZXQ\n" if i else "") + text
            for i, (_, text) in enumerate(batch)
        )
        translated = translator.translate(joined)
        parts = re.split(r"\s*ZXQSEP\d{4}ZXQ\s*", translated)
        if len(parts) != len(batch):
            parts = [translator.translate(text) for _, text in batch]
        for (target, source), result in zip(batch, parts, strict=True):
            output[target] = clean(result)
            cache[source] = output[target]
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def write_srt(path: Path, groups: list[dict], translations: list[str]) -> None:
    blocks = []
    for number, (group, text) in enumerate(zip(groups, translations, strict=True), 1):
        blocks.append(f"{number}\n{group['start']} --> {group['end']}\n{text}")
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def main() -> None:
    manifest = json.loads((DELIVERABLES / "manifest.json").read_text(encoding="utf-8"))
    BACKUP.mkdir(exist_ok=True)
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    translator = GoogleTranslator(source="ko", target="en")
    summary = []

    for item in manifest:
        folder = DELIVERABLES / f"{item['youtube_id']}-{item['slug']}"
        english = folder / "en-subtitles.srt"
        backup = BACKUP / f"{item['youtube_id']}-{item['slug']}.en-subtitles.srt"
        if not backup.exists():
            shutil.copy2(english, backup)
        groups = group_rows(parse_srt(folder / "ko-transcript.srt"))
        translations = translate_all(groups, translator, cache)
        write_srt(english, groups, translations)
        summary.append({"youtube_id": item["youtube_id"], "slug": item["slug"], "cues": len(groups)})
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{item['youtube_id']}: {len(groups)} context-aware cues", flush=True)

    (DELIVERABLES / "context-rewrite-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
