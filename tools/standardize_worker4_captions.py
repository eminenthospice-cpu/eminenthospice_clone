from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_PUBLIC_BYTES = int(23.5 * 1024 * 1024)


@dataclass(frozen=True)
class Job:
    video_id: str
    slug: str
    work_dir: Path
    stem: str
    archive_dir: Path
    youtube_dir: Path
    width: int
    height: int
    font_size: int
    outline: int
    margin_l: int
    margin_r: int
    margin_v: int
    max_chars: int

    @property
    def source_video(self) -> Path:
        return self.work_dir / f"{self.stem}_compressed.mp4"

    @property
    def srt(self) -> Path:
        return self.work_dir / f"{self.stem}_english.srt"

    @property
    def ass(self) -> Path:
        return self.work_dir / f"{self.stem}_english_clean.ass"

    @property
    def captioned_video(self) -> Path:
        return self.work_dir / f"{self.stem}_english_captioned.mp4"

    @property
    def public_video(self) -> Path:
        return ROOT / "public" / "videos" / f"{self.slug}.mp4"


JOBS = [
    Job(
        "xnI28GlZwZI",
        "american-hospice-nurse",
        ROOT / "deliverables" / "korean-video-xnI28GlZwZI",
        "TubePull_american_hospice_nurse",
        ROOT / "deliverables" / "subtitle-reference" / "xnI28GlZwZI-american-hospice-nurse",
        ROOT / "deliverables" / "youtube-subtitles" / "xnI28GlZwZI-american-hospice-nurse",
        640,
        360,
        13,
        1,
        60,
        60,
        26,
        96,
    ),
    Job(
        "Rv1Cbnb4QDA",
        "emergency-medications",
        ROOT / "deliverables" / "korean-video-Rv1Cbnb4QDA",
        "YTDown_YouTube_Media_Rv1Cbnb4QDA_001_1080p",
        ROOT / "deliverables" / "subtitle-reference" / "Rv1Cbnb4QDA-emergency-medications",
        ROOT / "deliverables" / "youtube-subtitles" / "Rv1Cbnb4QDA-emergency-medications",
        1280,
        720,
        24,
        2,
        120,
        120,
        52,
        84,
    ),
    Job(
        "2Ci1inVJrrc",
        "chaplain-perspective",
        ROOT / "deliverables" / "korean-video-2Ci1inVJrrc",
        "YTDown_YouTube_Media_2Ci1inVJrrc_001_1080p",
        ROOT / "deliverables" / "subtitle-reference" / "2Ci1inVJrrc-chaplain-perspective",
        ROOT / "deliverables" / "youtube-subtitles" / "2Ci1inVJrrc-chaplain-perspective",
        1280,
        720,
        24,
        2,
        120,
        120,
        52,
        84,
    ),
]


def run(args: list[str], cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def parse_time(raw: str) -> float:
    hours, minutes, seconds = raw.replace(",", ".").split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def srt_time(seconds: float) -> str:
    millis = round(max(0.0, seconds) * 1000)
    hours, rem = divmod(millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def ass_time(seconds: float) -> str:
    centis = round(max(0.0, seconds) * 100)
    hours, rem = divmod(centis, 360_000)
    minutes, rem = divmod(rem, 6_000)
    secs, cs = divmod(rem, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{cs:02d}"


def read_srt(path: Path) -> list[dict]:
    blocks = re.split(r"\r?\n\r?\n+", path.read_text(encoding="utf-8-sig").strip())
    cues = []
    for block in blocks:
        lines = block.splitlines()
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        start_raw, end_raw = [part.strip() for part in lines[timing_index].split("-->", 1)]
        text = " ".join(line.strip() for line in lines[timing_index + 1 :] if line.strip())
        text = re.sub(r"\s+", " ", text)
        for old in ("Kim Jung Ah", "Kim Jung-ah", "Kim Jeong-ah"):
            text = text.replace(old, "Kim Jeong Ah")
        if text:
            cues.append({"start": parse_time(start_raw), "end": parse_time(end_raw), "text": text})
    return cues


def split_words(text: str, max_chars: int) -> list[str]:
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if current and len(candidate) > max_chars:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        chunks.append(" ".join(current))
    return chunks


def balance_lines(text: str) -> str:
    words = text.split()
    if len(text) <= 38 or len(words) < 2:
        return text
    best = min(
        range(1, len(words)),
        key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))),
    )
    return " ".join(words[:best]) + "\n" + " ".join(words[best:])


def canonicalize(cues: list[dict], max_chars: int) -> list[dict]:
    expanded = []
    for cue in cues:
        chunks = split_words(cue["text"], max_chars)
        duration = max(0.01, cue["end"] - cue["start"])
        weights = [max(1, len(chunk)) for chunk in chunks]
        cursor = cue["start"]
        for index, chunk in enumerate(chunks):
            end = cue["end"] if index == len(chunks) - 1 else cursor + duration * weights[index] / sum(weights[index:])
            expanded.append({"start": cursor, "end": end, "text": balance_lines(chunk)})
            cursor = end
    for index, cue in enumerate(expanded):
        if index:
            cue["start"] = max(cue["start"], expanded[index - 1]["end"])
        if index + 1 < len(expanded):
            cue["end"] = min(cue["end"], expanded[index + 1]["start"])
        cue["end"] = max(cue["start"] + 0.01, cue["end"])
    return expanded


def write_srt(path: Path, cues: list[dict]) -> None:
    blocks = []
    for index, cue in enumerate(cues, 1):
        blocks.append(
            f"{index}\n{srt_time(cue['start'])} --> {srt_time(cue['end'])}\n{cue['text']}"
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def write_ass(job: Job, cues: list[dict]) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {job.width}
PlayResY: {job.height}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{job.font_size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,{job.outline},0,2,{job.margin_l},{job.margin_r},{job.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for cue in cues:
        text = cue["text"].replace("\n", r"\N")
        events.append(
            f"Dialogue: 0,{ass_time(cue['start'])},{ass_time(cue['end'])},Default,,0,0,0,,{text}"
        )
    job.ass.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def sync_archives(job: Job) -> None:
    job.archive_dir.mkdir(parents=True, exist_ok=True)
    job.youtube_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(job.srt, job.archive_dir / job.srt.name)
    shutil.copy2(job.ass, job.archive_dir / job.ass.name)
    shutil.copy2(job.srt, job.youtube_dir / "en-subtitles.srt")


def burn(job: Job) -> None:
    temp = job.captioned_video.with_name(job.captioned_video.stem + ".tmp.mp4")
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            job.source_video.name,
            "-vf",
            f"ass={job.ass.name}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            temp.name,
        ],
        cwd=job.work_dir,
    )
    temp.replace(job.captioned_video)


def public_encode(job: Job) -> None:
    temp = job.public_video.with_name(job.public_video.stem + ".tmp.mp4")
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(job.captioned_video),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "25",
            "-maxrate",
            "2400k",
            "-bufsize",
            "4800k",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-movflags",
            "+faststart",
            str(temp),
        ]
    )
    if temp.stat().st_size > MAX_PUBLIC_BYTES:
        duration = float(
            subprocess.check_output(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=nw=1:nk=1",
                    str(job.captioned_video),
                ],
                text=True,
            ).strip()
        )
        video_rate = max(180, int((MAX_PUBLIC_BYTES * 8 / duration / 1000) - 128))
        temp.unlink()
        passlog = job.work_dir / f"{job.video_id}-public-pass"
        common = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(job.captioned_video),
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-b:v",
            f"{video_rate}k",
            "-pix_fmt",
            "yuv420p",
            "-passlogfile",
            str(passlog),
        ]
        run(common + ["-pass", "1", "-an", "-f", "null", "NUL"])
        run(
            common
            + [
                "-pass",
                "2",
                "-c:a",
                "aac",
                "-b:a",
                "96k",
                "-movflags",
                "+faststart",
                str(temp),
            ]
        )
        for file in job.work_dir.glob(f"{passlog.name}*"):
            file.unlink()
    temp.replace(job.public_video)


def main() -> None:
    for job in JOBS:
        print(f"Standardizing {job.video_id}", flush=True)
        cues = canonicalize(read_srt(job.srt), job.max_chars)
        write_srt(job.srt, cues)
        write_ass(job, cues)
        sync_archives(job)
        burn(job)
        public_encode(job)
        print(f"Completed {job.video_id}: {len(cues)} cues", flush=True)


if __name__ == "__main__":
    main()
