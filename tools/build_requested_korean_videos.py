from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "Downloads"
JOBS = [
    {
        "id": "2Ci1inVJrrc", "topic": "chaplain-perspective",
        "video": DOWNLOADS / "YTDown_YouTube_Media_2Ci1inVJrrc_001_1080p.mp4",
        "base": "YTDown_YouTube_Media_2Ci1inVJrrc_001_1080p", "height": 720,
        "master": ROOT / "audit/caption_master/hospice-social-work-bereavement-interview-peter-park-korean-english-subtitles.json",
    },
    {
        "id": "Rv1Cbnb4QDA", "topic": "emergency-medications",
        "video": DOWNLOADS / "YTDown_YouTube_Media_Rv1Cbnb4QDA_001_1080p (1).mp4",
        "base": "YTDown_YouTube_Media_Rv1Cbnb4QDA_001_1080p", "height": 720,
    },
    {
        "id": "xnI28GlZwZI", "topic": "american-hospice-nurse",
        "video": next(DOWNLOADS.glob("[[]TubePull[]]*.mp4")),
        "base": "TubePull_american_hospice_nurse", "height": 360,
    },
]


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def seconds(value: str) -> float:
    h, m, s = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def stamp(value: float) -> str:
    ms = round(max(0, value) * 1000)
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def parse_srt(path: Path) -> list[dict]:
    rows = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            a, b = map(str.strip, lines[1].split("-->"))
            rows.append({"start": seconds(a), "end": seconds(b),
                         "text": " ".join(lines[2:]).strip()})
    return rows


def dedupe(rows: list[dict]) -> list[dict]:
    additions, previous = [], []
    for row in rows:
        words = row["text"].split()
        overlap = 0
        for n in range(min(len(previous), len(words)), 0, -1):
            if previous[-n:] == words[:n]:
                overlap = n
                break
        words = words[overlap:]
        if words and not re.fullmatch(r"[\[\(]?(음악|박수)[\]\)]?", " ".join(words)):
            additions.append({**row, "text": " ".join(words)})
        previous = row["text"].split()
    groups = []
    for row in additions:
        if (groups and row["end"] - groups[-1]["start"] <= 7.0
                and len(groups[-1]["text"] + " " + row["text"]) <= 82):
            groups[-1]["end"] = row["end"]
            groups[-1]["text"] += " " + row["text"]
        else:
            groups.append(row.copy())
    return groups


def translate(text: str, cache: dict) -> str:
    if text in cache:
        result = cache[text]
    else:
        query = urllib.parse.urlencode({"client": "gtx", "sl": "ko", "tl": "en", "dt": "t", "q": text})
        with urllib.request.urlopen("https://translate.googleapis.com/translate_a/single?" + query, timeout=30) as response:
            data = json.load(response)
        result = "".join(part[0] for part in data[0] if part[0])
        cache[text] = result
    fixes = [
        (r"\bhostesses?\b", "hospice"), (r"\bHospice Care\b", "hospice care"),
        (r"\bmorphing\b", "morphine"), (r"\bMora ?Jae ?Farm\b", "lorazepam"),
        (r"\bAtrofin\b", "atropine"), (r"\bTyrenol\b", "Tylenol"),
        (r"\bDucolax\b", "Dulcolax"), (r"\bcc\b", "mL"),
        (r"\bMantis (?:PC|Peace Care)\b", "Eminent Hospice Care"),
        (r"\bChinese character(s)?\b", r"patient\1"), (r"\binstructor\b", "nurse"),
        (r"\bMary Kay\b", "Medi-Cal"), (r"\bMedicare Part A\b", "Medicare Part A"),
        (r"0\.25 o'clock c", "0.25 mL"), (r"\bMedicare Palt A\b", "Medicare Part A"),
    ]
    for pattern, replacement in fixes:
        result = re.sub(pattern, replacement, result, flags=re.I)
    return re.sub(r"\s+", " ", result).strip()


def split_cue(row: dict) -> list[dict]:
    words = row["text"].split()
    if len(words) <= 14 and len(row["text"]) <= 78:
        return [row]
    mid = len(words) // 2
    for i in range(max(2, mid - 3), min(len(words) - 1, mid + 4)):
        if words[i - 1].endswith((",", ";", ":", ".", "?", "!")):
            mid = i
            break
    duration = row["end"] - row["start"]
    cut = row["start"] + duration * mid / len(words)
    return [{"start": row["start"], "end": cut, "text": " ".join(words[:mid])},
            {"start": cut, "end": row["end"], "text": " ".join(words[mid:])}]


def wrap(text: str, width: int) -> str:
    words, lines = text.split(), ["", ""]
    for word in words:
        target = 0 if not lines[1] and len((lines[0] + " " + word).strip()) <= width else 1
        lines[target] = (lines[target] + " " + word).strip()
    return "\n".join(x for x in lines if x)


def write_outputs(job: dict, ko: list[dict], en: list[dict], out: Path) -> tuple[Path, Path]:
    base = job["base"]
    for language, rows, suffix in (("Korean", ko, "korean_transcript"), ("English", en, "english_translation")):
        (out / f"{base}_{suffix}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / f"{base}_{suffix}.txt").write_text(
            "\n".join(f"[{stamp(x['start'])} --> {stamp(x['end'])}] {x['text']}" for x in rows) + "\n",
            encoding="utf-8")
    width = 42 if job["height"] == 720 else 34
    srt = out / f"{base}_english.srt"
    srt.write_text("\n\n".join(
        f"{i}\n{stamp(x['start'])} --> {stamp(x['end'])}\n{wrap(x['text'], width)}"
        for i, x in enumerate(en, 1)) + "\n", encoding="utf-8")
    font = 24 if job["height"] == 720 else 13
    play_x = 1280 if job["height"] == 720 else 640
    margin = 42 if job["height"] == 720 else 21
    ass = out / f"{base}_english_clean.ass"
    header = (
        f"[Script Info]\nScriptType: v4.00+\nPlayResX: {play_x}\nPlayResY: {job['height']}\n"
        "WrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Arial,{font},&H00FFFFFF,&H000000FF,&H90000000,&HC0000000,-1,0,0,0,"
        f"100,100,0,0,3,2,0,2,{margin},{margin},{margin},1\n\n[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    events = "\n".join(
        f"Dialogue: 0,{stamp(x['start']).replace(',', '.')[1:-1]},{stamp(x['end']).replace(',', '.')[1:-1]},"
        f"Default,,0,0,0,,{wrap(x['text'], width).replace(chr(10), r'\N')}" for x in en)
    ass.write_text(header + events + "\n", encoding="utf-8")
    return srt, ass


def main() -> None:
    cache_path = ROOT / "audit/youtube_translation_cache.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    for job in JOBS:
        source = ROOT / "deliverables/youtube-subtitles" / f"{job['id']}-{job['topic']}"
        out = ROOT / "deliverables" / f"korean-video-{job['id']}"
        out.mkdir(parents=True, exist_ok=True)
        ko = dedupe(parse_srt(source / "ko-transcript.srt"))
        if job.get("master"):
            en = json.loads(job["master"].read_text(encoding="utf-8"))["entries"]
            en = [{"start": x["start"], "end": x["end"], "text": x["text"]} for x in en]
        else:
            en = []
            for row in ko:
                en.extend(split_cue({**row, "text": translate(row["text"], cache)}))
        srt, ass = write_outputs(job, ko, en, out)
        compressed = out / f"{job['base']}_compressed.mp4"
        captioned = out / f"{job['base']}_english_captioned.mp4"
        scale = "scale=640:360" if job["height"] == 360 else "scale='min(1280,iw)':-2"
        run("ffmpeg", "-y", "-i", str(job["video"]), "-vf", scale, "-c:v", "libx264", "-preset", "medium",
            "-crf", "23", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(compressed))
        escaped = str(ass).replace("\\", "/").replace(":", r"\:")
        run("ffmpeg", "-y", "-i", str(compressed), "-vf", f"ass='{escaped}'", "-c:v", "libx264",
            "-preset", "medium", "-crf", "22", "-c:a", "copy", "-movflags", "+faststart", str(captioned))
        archive = ROOT / "deliverables/subtitle-reference" / f"{job['id']}-{job['topic']}"
        archive.mkdir(parents=True, exist_ok=True)
        for item in out.glob(f"{job['base']}_*"):
            if item.suffix.lower() in {".txt", ".json", ".srt", ".ass"}:
                shutil.copy2(item, archive / item.name)
        frames = out / "caption_verify_frames"
        frames.mkdir(exist_ok=True)
        for index, when in enumerate((20, 80, 140), 1):
            run("ffmpeg", "-y", "-ss", str(when), "-i", str(captioned), "-frames:v", "1",
                "-q:v", "2", str(frames / f"frame_{index:02}.jpg"))
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
