import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(r"C:\Users\emine\OneDrive\Desktop\Website_Clone")
DOWNLOADS = Path(r"C:\Users\emine\Downloads")
JOBS = [
    (
        "3mgBE6CaI4I",
        "end-of-life-timing",
        DOWNLOADS / "YTDown_YouTube_Media_3mgBE6CaI4I_001_720p.mp4",
    ),
    (
        "edmwae3Iglk",
        "nebulizer",
        DOWNLOADS / "YTDown_YouTube_Media_edmwae3Iglk_001_1080p (2).mp4",
    ),
    (
        "Vq5rIpelzhk",
        "oxygen-concentrator",
        DOWNLOADS / "YTDown_YouTube_Media_Vq5rIpelzhk_001_1080p (1).mp4",
    ),
]

MEDICAL_REPLACEMENTS = [
    (r"\bEminent Peace Care\b", "Eminent Hospice Care"),
    (r"\bEminent Hospice\b", "Eminent Hospice Care"),
    (r"\bhostess\b", "hospice"),
    (r"\boxygen machine\b", "oxygen concentrator"),
    (r"\bgas tank\b", "humidifier bottle"),
    (r"\bwater tank\b", "humidifier bottle"),
    (r"\bdisinfected distilled water\b", "sterile distilled water"),
    (r"\boxygen bottle\b", "oxygen tubing"),
    (r"\boxygen device\b", "oxygen concentrator"),
    (r"\bamount of oxygen\b", "oxygen flow rate"),
    (r"\bthe patient's soju\b", "the patient's nasal cannula"),
    (r"\bexpand the womb\b", "allow the lungs to expand"),
    (r"\b2l\b", "2 L/min"),
    (r"\b2 a\.m\.\b", "a comfortable fit"),
    (r"\bmedication infusion container\b", "nebulizer medication cup"),
    (r"\bmedication container\b", "medication cup"),
    (r"\bfill bottle lid\b", "medication cup lid"),
    (r"\bno gas\b", "no mist"),
    (r"\bdirect my stomach\b", "breathe out slowly"),
    (r"\bWhen will you return\?\b", "How much time does the patient have left?"),
    (r"\bpredicted life expectancy\b", "estimated life expectancy"),
]


def polish(text):
    text = text.replace("â€œ", '"').replace("â€", '"').replace("â€™", "'")
    for pattern, replacement in MEDICAL_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def stamp(value):
    h, m, rest = value.replace(".", ",").split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")[:3]) / 1000


def srt_stamp(value):
    ms = round(max(0, value) * 1000)
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def ass_stamp(value):
    cs = round(max(0, value) * 100)
    h, rem = divmod(cs, 360_000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02}:{s:02}.{cs:02}"


def parse_srt(path):
    blocks = re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig").strip())
    cues = []
    for block in blocks:
        lines = block.splitlines()
        timing = next((line for line in lines if "-->" in line), None)
        if not timing:
            continue
        pos = lines.index(timing)
        start, end = [stamp(part.strip()) for part in timing.split("-->")]
        text = re.sub(r"\s+", " ", " ".join(lines[pos + 1 :])).strip()
        if text and text.lower() not in {"ah", "ahhh", "ah ah ah ah", "[music]"}:
            cues.append({"start": start, "end": end, "text": polish(text)})
    return cues


def split_text(text, limit=76):
    if len(text) <= limit:
        return [text]
    parts = re.split(r"(?<=[.!?;:])\s+|(?<=,)\s+", text)
    chunks, current = [], ""
    for part in parts:
        candidate = f"{current} {part}".strip()
        if current and len(candidate) > limit:
            chunks.append(current)
            current = part
        else:
            current = candidate
    if current:
        chunks.append(current)
    final = []
    for chunk in chunks:
        words = chunk.split()
        while len(" ".join(words)) > limit:
            cut = max(i for i in range(1, len(words)) if len(" ".join(words[:i])) <= limit)
            final.append(" ".join(words[:cut]))
            words = words[cut:]
        if words:
            final.append(" ".join(words))
    return final


def balance(text, width=42):
    if len(text) <= width:
        return text
    words = text.split()
    options = []
    for i in range(1, len(words)):
        left, right = " ".join(words[:i]), " ".join(words[i:])
        if len(left) <= width and len(right) <= width:
            options.append((abs(len(left) - len(right)), left, right))
    if not options:
        return text
    _, left, right = min(options)
    return left + "\n" + right


def clean_timing(cues, duration):
    result = []
    for index, cue in enumerate(cues):
        start = cue["start"]
        next_start = cues[index + 1]["start"] if index + 1 < len(cues) else min(cue["end"], duration)
        end = min(cue["end"], next_start, duration)
        if end - start < 0.8:
            end = min(next_start, duration, start + 0.8)
        pieces = split_text(cue["text"])
        available = max(0.5, end - start)
        weights = [max(1, len(piece)) for piece in pieces]
        total = sum(weights)
        cursor = start
        for piece_index, (piece, weight) in enumerate(zip(pieces, weights)):
            piece_end = end if piece_index == len(pieces) - 1 else cursor + available * weight / total
            result.append({"start": cursor, "end": piece_end, "text": piece})
            cursor = piece_end
    return [cue for cue in result if cue["end"] - cue["start"] >= 0.35]


def write_srt(path, cues):
    blocks = []
    for i, cue in enumerate(cues, 1):
        blocks.append(
            f"{i}\n{srt_stamp(cue['start'])} --> {srt_stamp(cue['end'])}\n{balance(cue['text'])}"
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def write_ass(path, cues):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Clean,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,0,0,3,1,0,2,72,72,42,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = []
    for cue in cues:
        text = balance(cue["text"]).replace("\n", r"\N").replace(",", r"\,")
        lines.append(
            f"Dialogue: 0,{ass_stamp(cue['start'])},{ass_stamp(cue['end'])},Clean,,0,0,0,,{text}"
        )
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8-sig")


def write_json(path, cues):
    path.write_text(json.dumps(cues, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe_duration(video):
    command = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(video),
    ]
    return float(subprocess.check_output(command, text=True).strip())


def main():
    for video_id, slug, source in JOBS:
        if not source.exists():
            raise FileNotFoundError(source)
        source_subs = ROOT / "deliverables" / "youtube-subtitles" / f"{video_id}-{slug}"
        output = ROOT / "deliverables" / f"korean-video-{video_id}"
        archive = ROOT / "deliverables" / "subtitle-reference" / f"{video_id}-{slug}"
        output.mkdir(parents=True, exist_ok=True)
        archive.mkdir(parents=True, exist_ok=True)
        duration = probe_duration(source)
        base = source.stem

        en_cues = clean_timing(parse_srt(source_subs / "en-subtitles.srt"), duration)
        clean_srt = output / f"{base}_english_clean.srt"
        clean_ass = output / f"{base}_english_clean.ass"
        write_srt(clean_srt, en_cues)
        write_ass(clean_ass, en_cues)

        ko_cues = parse_srt(source_subs / "ko-transcript.srt")
        shutil.copy2(source_subs / "ko-transcript.srt", output / f"{base}_korean_transcript.srt")
        shutil.copy2(source_subs / "ko-transcript.txt", output / f"{base}_korean_transcript.txt")
        write_json(output / f"{base}_korean_transcript.json", ko_cues)
        write_json(output / f"{base}_english_translation.json", en_cues)
        (output / f"{base}_english_translation.txt").write_text(
            "\n".join(f"[{srt_stamp(c['start'])[:-4]}] {c['text']}" for c in en_cues) + "\n",
            encoding="utf-8",
        )
        for item in output.glob(f"{base}_*"):
            if item.is_file():
                shutil.copy2(item, archive / item.name)
        print(f"{video_id}|{duration:.3f}|{len(en_cues)}|{output}", flush=True)


if __name__ == "__main__":
    main()
