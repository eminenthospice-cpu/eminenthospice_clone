import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(r"C:\Users\emine\OneDrive\Desktop\Website_Clone")
CAP_BYTES = int(23.5 * 1024 * 1024)
TARGET_BYTES = int(22.8 * 1024 * 1024)
JOBS = {
    "9g98EDnOAUI": {
        "slug": "suction-machine",
        "base": "YTDown_YouTube_Media_9g98EDnOAUI_001_1080p",
    },
    "qWl3XdJ4rck": {
        "slug": "hospice-aide-perspective",
        "base": "YTDown_YouTube_Media_qWl3XdJ4rck_001_1080p",
    },
    "jsPCywsMe5Y": {
        "slug": "hospice-nurse-perspective",
        "base": "YTDown_YouTube_Media_jsPCywsMe5Y_001_1080p",
    },
}
NAME_VARIANTS = re.compile(r"\b(?:Kim Jung Ah|Kim Jung-ah|Kim Jeong-ah)\b")
MAX_LINE = 42
MAX_CUE_CHARS = 76


def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)


def capture(*args):
    return subprocess.check_output([str(arg) for arg in args], text=True).strip()


def parse_stamp(value):
    hours, minutes, tail = value.replace(".", ",").split(":")
    seconds, millis = tail.split(",")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(millis.ljust(3, "0")[:3]) / 1000
    )


def srt_stamp(seconds):
    millis = round(max(0, seconds) * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    seconds, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def ass_stamp(seconds):
    centis = round(max(0, seconds) * 100)
    hours, centis = divmod(centis, 360_000)
    minutes, centis = divmod(centis, 6000)
    seconds, centis = divmod(centis, 100)
    return f"{hours}:{minutes:02}:{seconds:02}.{centis:02}"


def parse_srt(path):
    cues = []
    blocks = re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig").strip())
    for block in blocks:
        lines = block.splitlines()
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        start, end = [
            parse_stamp(value.strip())
            for value in lines[timing_index].split("-->")
        ]
        text = " ".join(line.strip() for line in lines[timing_index + 1 :] if line.strip())
        text = NAME_VARIANTS.sub("Kim Jeong Ah", re.sub(r"\s+", " ", text).strip())
        cues.append({"start": start, "end": end, "text": text})
    return cues


def split_text(text):
    if len(text) <= MAX_CUE_CHARS:
        return [text]
    pieces = re.split(r"(?<=[.!?;:])\s+|(?<=,)\s+", text)
    chunks = []
    current = ""
    for piece in pieces:
        candidate = f"{current} {piece}".strip()
        if current and len(candidate) > MAX_CUE_CHARS:
            chunks.append(current)
            current = piece
        else:
            current = candidate
    if current:
        chunks.append(current)
    final = []
    for chunk in chunks:
        words = chunk.split()
        while len(" ".join(words)) > MAX_CUE_CHARS:
            possible = [
                i
                for i in range(1, len(words))
                if len(" ".join(words[:i])) <= MAX_CUE_CHARS
            ]
            if not possible:
                break
            cut = max(possible)
            final.append(" ".join(words[:cut]))
            words = words[cut:]
        if words:
            final.append(" ".join(words))
    return final


def balance(text):
    if len(text) <= MAX_LINE:
        return text
    words = text.split()
    options = []
    for index in range(1, len(words)):
        left = " ".join(words[:index])
        right = " ".join(words[index:])
        if len(left) <= MAX_LINE and len(right) <= MAX_LINE:
            options.append((abs(len(left) - len(right)), left, right))
    if not options:
        raise ValueError(f"Cannot balance into two lines: {text}")
    _, left, right = min(options)
    return f"{left}\n{right}"


def canonicalize(cues, duration):
    canonical = []
    for index, cue in enumerate(cues):
        start = max(0, cue["start"])
        next_start = cues[index + 1]["start"] if index + 1 < len(cues) else duration
        end = min(cue["end"], next_start, duration)
        if end <= start:
            raise ValueError(f"Invalid cue timing at {start:.3f}")
        pieces = split_text(cue["text"])
        weights = [max(1, len(piece)) for piece in pieces]
        total_weight = sum(weights)
        cursor = start
        for piece_index, (piece, weight) in enumerate(zip(pieces, weights)):
            piece_end = (
                end
                if piece_index == len(pieces) - 1
                else cursor + (end - start) * weight / total_weight
            )
            if piece_end - cursor < 0.25:
                raise ValueError(f"Split cue is too short at {cursor:.3f}")
            canonical.append(
                {"start": cursor, "end": piece_end, "text": piece}
            )
            cursor = piece_end
    return canonical


def write_srt(path, cues):
    blocks = []
    for index, cue in enumerate(cues, 1):
        blocks.append(
            f"{index}\n{srt_stamp(cue['start'])} --> {srt_stamp(cue['end'])}"
            f"\n{balance(cue['text'])}"
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def ass_header():
    return """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Clean,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""


def write_ass(path, cues, synthetic=False):
    lines = []
    for index, cue in enumerate(cues):
        start = index + 0.05 if synthetic else cue["start"]
        end = index + 0.95 if synthetic else cue["end"]
        text = balance(cue["text"]).replace("\n", r"\N")
        lines.append(
            f"Dialogue: 0,{ass_stamp(start)},{ass_stamp(end)},Clean,,0,0,0,,{text}"
        )
    path.write_text(ass_header() + "\n".join(lines) + "\n", encoding="utf-8-sig")


def ffmpeg_filter_path(path):
    return path.resolve().as_posix().replace(":", r"\:")


def probe(video):
    raw = capture(
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,codec_name,width,height",
        "-of",
        "json",
        video,
    )
    return json.loads(raw)


def burn_master(source, ass, output):
    temp = output.with_suffix(".rebuild.mp4")
    run(
        "ffmpeg",
        "-y",
        "-i",
        source,
        "-vf",
        f"ass='{ffmpeg_filter_path(ass)}'",
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
        temp,
    )
    temp.replace(output)


def encode_public(master, output):
    duration = float(probe(master)["format"]["duration"])
    source_size = master.stat().st_size
    temp = output.with_suffix(".rebuild.mp4")
    if source_size <= TARGET_BYTES:
        shutil.copy2(master, temp)
    else:
        audio_kbps = 128
        video_kbps = max(
            350,
            math.floor((TARGET_BYTES * 8 / duration) / 1000 - audio_kbps - 12),
        )
        passlog = output.parent / f".{output.stem}-worker3-pass"
        run(
            "ffmpeg",
            "-y",
            "-i",
            master,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-b:v",
            f"{video_kbps}k",
            "-pass",
            "1",
            "-passlogfile",
            passlog,
            "-f",
            "mp4",
            "NUL",
        )
        run(
            "ffmpeg",
            "-y",
            "-i",
            master,
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-b:v",
            f"{video_kbps}k",
            "-pass",
            "2",
            "-passlogfile",
            passlog,
            "-c:a",
            "aac",
            "-b:a",
            f"{audio_kbps}k",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            temp,
        )
        for leftover in output.parent.glob(f"{passlog.name}*"):
            leftover.unlink()
    if temp.stat().st_size > CAP_BYTES:
        raise ValueError(f"Public encode exceeds cap: {temp.stat().st_size}")
    temp.replace(output)


def render_and_qa(output_dir, cues):
    qa_dir = output_dir / "canonical_caption_qa"
    if qa_dir.exists():
        shutil.rmtree(qa_dir)
    qa_dir.mkdir()
    synthetic_ass = qa_dir / "all-cues.ass"
    write_ass(synthetic_ass, cues, synthetic=True)
    run(
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        f"color=c=0x00FF00:s=1280x720:d={len(cues)}:r=1",
        "-vf",
        f"ass='{ffmpeg_filter_path(synthetic_ass)}'",
        "-frames:v",
        len(cues),
        qa_dir / "cue-%04d.png",
    )
    minimum_tops = []
    for frame in sorted(qa_dir.glob("cue-*.png")):
        image = Image.open(frame).convert("RGB")
        pixels = image.load()
        changed = [
            y
            for y in range(image.height)
            if any(pixels[x, y] != (0, 255, 0) for x in range(image.width))
        ]
        if not changed:
            raise ValueError(f"No subtitle pixels in {frame.name}")
        top = min(changed)
        if top < 504:
            raise ValueError(f"{frame.name} starts at y={top}")
        minimum_tops.append(top)
    longest = sorted(
        range(len(cues)), key=lambda i: len(cues[i]["text"]), reverse=True
    )[:3]
    for rank, cue_index in enumerate(longest, 1):
        shutil.copy2(
            qa_dir / f"cue-{cue_index + 1:04}.png",
            qa_dir / f"longest-{rank}-cue-{cue_index + 1:04}.png",
        )
    return min(minimum_tops), longest


def static_qa(cues, ass):
    prohibited = re.compile(r"\b(?:Kim Jung Ah|Kim Jung-ah|Kim Jeong-ah)\b")
    for index, cue in enumerate(cues):
        lines = balance(cue["text"]).splitlines()
        if len(lines) > 2 or any(len(line) > MAX_LINE for line in lines):
            raise ValueError(f"Cue {index + 1} line violation")
        if index and cue["start"] < cues[index - 1]["end"] - 0.001:
            raise ValueError(f"Cue {index + 1} overlaps")
        if prohibited.search(cue["text"]):
            raise ValueError(f"Cue {index + 1} has prohibited name")
    style = (
        "Style: Clean,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,"
        "&H00000000,-1,0,0,0,100,100,0,0,3,2,0,2,120,120,52,1"
    )
    if style not in ass.read_text(encoding="utf-8-sig"):
        raise ValueError("ASS style does not match canonical style")


def update_text_artifacts(output_dir, base, cues):
    (output_dir / f"{base}_english_translation.txt").write_text(
        "\n".join(
            f"[{srt_stamp(cue['start'])[:-4]}] {cue['text']}" for cue in cues
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / f"{base}_english_translation.json").write_text(
        json.dumps(cues, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main():
    report = {}
    for video_id, job in JOBS.items():
        output_dir = ROOT / "deliverables" / f"korean-video-{video_id}"
        archive = (
            ROOT
            / "deliverables"
            / "subtitle-reference"
            / f"{video_id}-{job['slug']}"
        )
        youtube = (
            ROOT
            / "deliverables"
            / "youtube-subtitles"
            / f"{video_id}-{job['slug']}"
        )
        source = output_dir / f"{job['base']}_compressed.mp4"
        srt = output_dir / f"{job['base']}_english.srt"
        ass = output_dir / f"{job['base']}_english_clean.ass"
        master = output_dir / f"{job['base']}_english_captioned.mp4"
        public = ROOT / "public" / "videos" / f"{job['slug']}.mp4"
        duration = float(probe(source)["format"]["duration"])
        cues = canonicalize(parse_srt(srt), duration)

        write_srt(srt, cues)
        write_ass(ass, cues)
        update_text_artifacts(output_dir, job["base"], cues)
        static_qa(cues, ass)
        min_top, longest = render_and_qa(output_dir, cues)
        burn_master(source, ass, master)
        encode_public(master, public)

        archive.mkdir(parents=True, exist_ok=True)
        youtube.mkdir(parents=True, exist_ok=True)
        for artifact in (
            srt,
            ass,
            output_dir / f"{job['base']}_english_translation.txt",
            output_dir / f"{job['base']}_english_translation.json",
        ):
            shutil.copy2(artifact, archive / artifact.name)
        shutil.copy2(srt, youtube / "en-subtitles.srt")

        source_probe = probe(source)
        master_probe = probe(master)
        public_probe = probe(public)
        durations = [
            float(item["format"]["duration"])
            for item in (source_probe, master_probe, public_probe)
        ]
        if max(durations) - min(durations) > 0.12:
            raise ValueError(f"Duration mismatch for {video_id}: {durations}")
        for label, item in (("master", master_probe), ("public", public_probe)):
            streams = item["streams"]
            codecs = {stream["codec_type"]: stream["codec_name"] for stream in streams}
            if codecs.get("video") != "h264" or codecs.get("audio") != "aac":
                raise ValueError(f"{label} codecs invalid for {video_id}: {codecs}")
        report[video_id] = {
            "slug": job["slug"],
            "cues": len(cues),
            "minimum_caption_y": min_top,
            "longest_cue_indexes": [index + 1 for index in longest],
            "source_duration": durations[0],
            "master_duration": durations[1],
            "public_duration": durations[2],
            "master_bytes": master.stat().st_size,
            "public_bytes": public.stat().st_size,
            "srt": str(srt),
            "ass": str(ass),
            "master": str(master),
            "public": str(public),
        }
        print(json.dumps({video_id: report[video_id]}, indent=2), flush=True)
    report_path = ROOT / "deliverables" / "worker3-caption-standardization-qa.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
