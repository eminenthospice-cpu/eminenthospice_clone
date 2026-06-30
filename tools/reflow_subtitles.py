import argparse
import re
from pathlib import Path


TIME_RE = re.compile(
    r"(?P<sh>\d{2}):(?P<sm>\d{2}):(?P<ss>\d{2}),(?P<sms>\d{3})"
    r" --> "
    r"(?P<eh>\d{2}):(?P<em>\d{2}):(?P<es>\d{2}),(?P<ems>\d{3})"
)


def seconds(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def stamp(value, separator=","):
    millis = round(max(0, value) * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def parse_srt(path):
    cues = []
    for block in re.split(r"\r?\n\r?\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        match = TIME_RE.fullmatch(lines[1].strip())
        if not match:
            raise ValueError(f"Invalid SRT block: {block[:80]}")
        values = match.groupdict()
        cues.append(
            {
                "start": seconds(values["sh"], values["sm"], values["ss"], values["sms"]),
                "end": seconds(values["eh"], values["em"], values["es"], values["ems"]),
                "text": re.sub(r"\s+", " ", " ".join(lines[2:])).strip(),
            }
        )
    return cues


def split_text(text, limit=108):
    if len(text) <= limit:
        return [text]

    parts = re.split(r"(?<=[.!?;,])\s+", text)
    chunks = []
    current = ""
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


def expand_cues(cues):
    expanded = []
    for cue in cues:
        chunks = split_text(cue["text"])
        if len(chunks) == 1:
            expanded.append(cue)
            continue

        duration = cue["end"] - cue["start"]
        weights = [max(1, len(chunk.replace(" ", ""))) for chunk in chunks]
        cursor = cue["start"]
        total = sum(weights)
        for index, (chunk, weight) in enumerate(zip(chunks, weights)):
            end = cue["end"] if index == len(chunks) - 1 else cursor + duration * weight / total
            expanded.append({"start": cursor, "end": end, "text": chunk})
            cursor = end
    return expanded


def balanced_lines(text):
    if len(text) <= 58:
        return [text]
    words = text.split()
    best = None
    for cut in range(1, len(words)):
        left = " ".join(words[:cut])
        right = " ".join(words[cut:])
        if max(len(left), len(right)) <= 62:
            score = abs(len(left) - len(right))
            if best is None or score < best[0]:
                best = (score, left, right)
    if best:
        return [best[1], best[2]]
    raise ValueError(f"Caption cannot fit in two lines: {text}")


def write_srt(cues, path):
    blocks = []
    for index, cue in enumerate(cues, 1):
        text = "\n".join(balanced_lines(cue["text"]))
        blocks.append(
            f"{index}\n{stamp(cue['start'])} --> {stamp(cue['end'])}\n{text}"
        )
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def ass_time(value):
    centis = round(max(0, value) * 100)
    hours, centis = divmod(centis, 360_000)
    minutes, centis = divmod(centis, 6_000)
    secs, centis = divmod(centis, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def write_ass(cues, path):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,27,&H00FFFFFF,&H000000FF,&H78000000,&H78000000,0,0,0,0,100,100,0,0,3,7,0,2,35,35,118,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for cue in cues:
        text = r"\N".join(balanced_lines(cue["text"]))
        events.append(
            f"Dialogue: 0,{ass_time(cue['start'])},{ass_time(cue['end'])},"
            f"Default,,0,0,0,,{text}"
        )
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--srt", type=Path, required=True)
    parser.add_argument("--ass", type=Path, required=True)
    args = parser.parse_args()

    cues = expand_cues(parse_srt(args.source))
    write_srt(cues, args.srt)
    write_ass(cues, args.ass)
    print(f"Wrote {len(cues)} cues with a maximum of two lines each.")


if __name__ == "__main__":
    main()
