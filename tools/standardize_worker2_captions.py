from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FFMPEG = ROOT / "tools" / "ffmpeg.exe"
FFPROBE = ROOT / "tools" / "ffprobe.exe"
MAX_PUBLIC_BYTES = int(23.5 * 1024 * 1024)

JOBS = [
    {
        "id": "SNGsCjicC8E",
        "topic": "SNGsCjicC8E-after-death-non-hospice",
        "public": "after-death-non-hospice-polst.mp4",
    },
    {
        "id": "3mgBE6CaI4I",
        "topic": "3mgBE6CaI4I-end-of-life-timing",
        "public": "end-of-life-timing.mp4",
    },
    {
        "id": "edmwae3Iglk",
        "topic": "edmwae3Iglk-nebulizer",
        "public": "nebulizer.mp4",
    },
    {
        "id": "Vq5rIpelzhk",
        "topic": "Vq5rIpelzhk-oxygen-concentrator",
        "public": "oxygen-concentrator.mp4",
    },
]


@dataclass
class Cue:
    start: float
    end: float
    text: str


def run(args: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(
        args, cwd=cwd, check=True, text=True, encoding="utf-8",
        errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return result.stdout


def ass_time(value: str) -> float:
    h, m, s = value.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def fmt_ass(value: float) -> str:
    value = max(0.0, value)
    h = int(value // 3600)
    m = int(value % 3600 // 60)
    s = value % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def fmt_srt(value: float) -> str:
    total_ms = max(0, round(value * 1000))
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def clean_text(value: str) -> str:
    value = re.sub(r"\{[^}]*\}", "", value)
    value = value.replace(r"\N", " ").replace(r"\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    for old in ("Kim Jung Ah", "Kim Jung-ah", "Kim Jeong-ah"):
        value = value.replace(old, "Kim Jeong Ah")
    return value


def parse_ass(path: Path) -> list[Cue]:
    cues: list[Cue] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("Dialogue:"):
            continue
        fields = line.split(",", 9)
        cues.append(Cue(ass_time(fields[1]), ass_time(fields[2]), clean_text(fields[9])))
    return cues


def balanced_lines(text: str, max_chars: int = 43) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    if len(text) <= max_chars:
        return [text]
    best: tuple[int, str, str] | None = None
    for i in range(1, len(words)):
        left, right = " ".join(words[:i]), " ".join(words[i:])
        if len(left) <= max_chars and len(right) <= max_chars:
            score = abs(len(left) - len(right))
            if best is None or score < best[0]:
                best = (score, left, right)
    if best:
        return [best[1], best[2]]
    return [text]


def split_text(text: str, max_total: int = 86) -> list[str]:
    if len(text) <= max_total:
        return [text]
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > max_total:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def canonicalize(source: list[Cue]) -> list[Cue]:
    result: list[Cue] = []
    for cue in source:
        parts = split_text(cue.text)
        weights = [max(1, len(part)) for part in parts]
        total = sum(weights)
        cursor = cue.start
        for index, (part, weight) in enumerate(zip(parts, weights)):
            end = cue.end if index == len(parts) - 1 else cursor + (cue.end - cue.start) * weight / total
            lines = balanced_lines(part)
            if len(lines) > 2 or any(len(line) > 43 for line in lines):
                raise ValueError(f"Unable to reflow: {part}")
            result.append(Cue(cursor, end, r"\N".join(lines)))
            cursor = end
    for index, cue in enumerate(result):
        if index and cue.start < result[index - 1].end:
            cue.start = result[index - 1].end
        if cue.end <= cue.start:
            raise ValueError(f"Non-positive cue at {cue.start}")
    return result


def write_srt(path: Path, cues: list[Cue]) -> None:
    blocks = []
    for index, cue in enumerate(cues, 1):
        blocks.append(
            f"{index}\n{fmt_srt(cue.start)} --> {fmt_srt(cue.end)}\n"
            f"{cue.text.replace(chr(92) + 'N', chr(10))}"
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def write_ass(path: Path, cues: list[Cue]) -> None:
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = [
        f"Dialogue: 0,{fmt_ass(c.start)},{fmt_ass(c.end)},Default,,0,0,0,,{c.text}"
        for c in cues
    ]
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8-sig")


def probe(path: Path) -> dict:
    return json.loads(run([
        str(FFPROBE), "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path)
    ]))


def burn(source: Path, ass: Path, output: Path, crf: str) -> None:
    temp = output.with_name(output.stem + ".tmp.mp4")
    if temp.exists():
        temp.unlink()
    run([
        str(FFMPEG), "-y", "-i", source.name, "-vf", f"ass={ass.name}",
        "-c:v", "libx264", "-preset", "medium", "-crf", crf,
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", temp.name
    ], cwd=source.parent)
    temp.replace(output)


def public_encode(master: Path, output: Path, duration: float) -> None:
    audio_kbps = 96
    target_bytes = int(22.8 * 1024 * 1024)
    video_kbps = max(300, int((target_bytes * 8 / duration / 1000) - audio_kbps - 12))
    temp = output.with_name(output.stem + ".tmp.mp4")
    passlog = output.parent / f".{output.stem}-worker2"
    common = [
        "-i", str(master), "-c:v", "libx264", "-preset", "medium",
        "-b:v", f"{video_kbps}k", "-maxrate", f"{int(video_kbps * 1.25)}k",
        "-bufsize", f"{video_kbps * 2}k", "-pix_fmt", "yuv420p",
    ]
    run([str(FFMPEG), "-y", *common, "-pass", "1", "-passlogfile", str(passlog),
         "-an", "-f", "mp4", "NUL"])
    run([str(FFMPEG), "-y", *common, "-pass", "2", "-passlogfile", str(passlog),
         "-c:a", "aac", "-b:a", f"{audio_kbps}k", "-movflags", "+faststart", str(temp)])
    for extra in output.parent.glob(f".{output.stem}-worker2*"):
        extra.unlink(missing_ok=True)
    if temp.stat().st_size > MAX_PUBLIC_BYTES:
        raise ValueError(f"Public encode too large: {temp.stat().st_size}")
    temp.replace(output)


def render_longest(ass: Path, cues: list[Cue], output: Path) -> None:
    longest = max(cues, key=lambda cue: max(map(len, cue.text.split(r"\N"))))
    output.parent.mkdir(exist_ok=True)
    run([
        str(FFMPEG), "-y", "-f", "lavfi", "-i",
        f"color=c=white:s=1280x720:d={max(1, longest.end + 0.1):.3f}",
        "-vf", f"ass={ass.name}", "-ss", f"{(longest.start + longest.end) / 2:.3f}",
        "-frames:v", "1", str(output)
    ], cwd=ass.parent)


def validate(cues: list[Cue], ass: Path) -> None:
    prohibited = ("Kim Jung Ah", "Kim Jung-ah", "Kim Jeong-ah")
    for index, cue in enumerate(cues):
        lines = cue.text.split(r"\N")
        assert len(lines) <= 2
        assert not any(term in cue.text for term in prohibited)
        if index:
            assert cue.start >= cues[index - 1].end - 0.001
    content = ass.read_text(encoding="utf-8-sig")
    expected = "Style: Default,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1"
    assert expected in content
    assert "PlayResX: 1280" in content and "PlayResY: 720" in content
    assert "WrapStyle: 2" in content


def main() -> None:
    report = {}
    for job in JOBS:
        folder = ROOT / "deliverables" / f"korean-video-{job['id']}"
        source = next(folder.glob("*_compressed.mp4"))
        old_ass = next(folder.glob("*_english_clean.ass"))
        stem = source.name.removesuffix("_compressed.mp4")
        canonical_srt = folder / f"{stem}_english_clean.srt"
        canonical_ass = folder / f"{stem}_english_clean.ass"
        master = folder / f"{stem}_english_captioned.mp4"

        cues = canonicalize(parse_ass(old_ass))
        write_srt(canonical_srt, cues)
        write_ass(canonical_ass, cues)
        validate(cues, canonical_ass)

        burn(source, canonical_ass, master, "20")
        source_info = probe(source)
        master_info = probe(master)
        duration = float(source_info["format"]["duration"])
        public = ROOT / "public" / "videos" / job["public"]
        public_encode(master, public, duration)
        public_info = probe(public)

        ref = ROOT / "deliverables" / "subtitle-reference" / job["topic"]
        ref.mkdir(exist_ok=True)
        shutil.copy2(canonical_srt, ref / canonical_srt.name)
        shutil.copy2(canonical_ass, ref / canonical_ass.name)
        if job["id"] == "SNGsCjicC8E":
            duplicate = ROOT / "deliverables" / "subtitle-reference" / "SNGsCjicC8E"
            shutil.copy2(canonical_srt, duplicate / canonical_srt.name)
            shutil.copy2(canonical_ass, duplicate / canonical_ass.name)

        youtube = ROOT / "deliverables" / "youtube-subtitles" / job["topic"]
        shutil.copy2(canonical_srt, youtube / "en-subtitles.srt")

        frame = folder / "caption_verify_frames" / "standardized_longest.png"
        render_longest(canonical_ass, cues, frame)
        src_streams = {s["codec_type"]: s for s in source_info["streams"]}
        master_streams = {s["codec_type"]: s for s in master_info["streams"]}
        public_streams = {s["codec_type"]: s for s in public_info["streams"]}
        assert master_streams["video"]["codec_name"] == "h264"
        assert master_streams["audio"]["codec_name"] == "aac"
        assert public_streams["video"]["codec_name"] == "h264"
        assert public_streams["audio"]["codec_name"] == "aac"
        assert abs(float(master_info["format"]["duration"]) - duration) < 0.15
        assert abs(float(public_info["format"]["duration"]) - duration) < 0.15

        report[job["id"]] = {
            "cues": len(cues),
            "max_lines": max(len(c.text.split(r"\N")) for c in cues),
            "overlaps": 0,
            "prohibited_name_variants": 0,
            "source_duration": duration,
            "master_duration": float(master_info["format"]["duration"]),
            "public_duration": float(public_info["format"]["duration"]),
            "resolution": [
                master_streams["video"]["width"], master_streams["video"]["height"]
            ],
            "source_audio": src_streams["audio"]["codec_name"],
            "master_codecs": ["h264", "aac"],
            "public_bytes": public.stat().st_size,
            "frame": str(frame),
        }
    report_path = ROOT / "deliverables" / "worker2-caption-standardization-QA.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
