import json
import re
import sys
from pathlib import Path

ROOT = Path(r"C:\Users\emine\OneDrive\Desktop\Website_Clone")
for pkg in (
    ROOT / ".codex_audio_pkgs",
    ROOT / "audio_pkgs",
    Path(r"C:\Users\emine\AppData\Local\Temp\codex_audio_pkgs"),
):
    if pkg.exists():
        sys.path.insert(0, str(pkg))

from faster_whisper import WhisperModel


VIDEO = ROOT / "deliverables" / "korean-video-42r5f9uf-0U" / "YTDown_YouTube_Media_42r5f9uf-0U_001_1080p_compressed.mp4"
OUT_DIR = VIDEO.parent
BASE = "YTDown_YouTube_Media_42r5f9uf-0U_001_1080p"
MODEL_DIR = ROOT / ".whisper_models"

GLOSSARY = """
Eminent Hospice Care, 김정아, hospice, POLST, Physician Orders for Life-Sustaining Treatment,
CPR, DNR, advance directive, Medicare, Medi-Cal, RN, LVN, nurse practitioner, chaplain,
bereavement care, morphine, lorazepam, atropine, acetaminophen, Dulcolax, nebulizer,
oxygen concentrator, nasal cannula, suction machine, suction catheter, nasogastric tube, feeding tube
"""


def fmt_txt(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def fmt_srt(seconds: float) -> str:
    ms = int(round(max(0.0, seconds) * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def wrap_caption(text: str, width: int = 42) -> str:
    words = compact(text).split()
    if not words:
        return ""
    lines = []
    line = words[0]
    for word in words[1:]:
        if len(line) + 1 + len(word) <= width:
            line += " " + word
        else:
            lines.append(line)
            line = word
    lines.append(line)
    if len(lines) <= 2:
        return "\n".join(lines)
    mid = (len(words) + 1) // 2
    return " ".join(words[:mid]) + "\n" + " ".join(words[mid:])


def merge_short_segments(items, target_min=1.2, target_max=6.8):
    merged = []
    cur = None
    for item in items:
        text = compact(item["text"])
        if not text:
            continue
        if cur is None:
            cur = {"start": item["start"], "end": item["end"], "text": text}
            continue
        cur_len = cur["end"] - cur["start"]
        combined = compact(cur["text"] + " " + text)
        if cur_len < target_min or (item["end"] - cur["start"] <= target_max and len(combined) <= 92):
            cur["end"] = item["end"]
            cur["text"] = combined
        else:
            merged.append(cur)
            cur = {"start": item["start"], "end": item["end"], "text": text}
    if cur:
        merged.append(cur)
    return merged


def transcribe(model, task):
    segments_iter, info = model.transcribe(
        str(VIDEO),
        language="ko",
        task=task,
        beam_size=1,
        best_of=1,
        temperature=0,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        initial_prompt=GLOSSARY,
    )
    segments = [
        {"start": seg.start, "end": seg.end, "text": compact(seg.text)}
        for seg in segments_iter
        if compact(seg.text)
    ]
    return info, merge_short_segments(segments)


def main():
    if not VIDEO.exists():
        raise SystemExit(f"Missing compressed video: {VIDEO}")

    model = WhisperModel("small", device="cpu", compute_type="int8", download_root=str(MODEL_DIR))
    ko_info, ko_segments = transcribe(model, "transcribe")

    (OUT_DIR / f"{BASE}_korean_transcript.json").write_text(
        json.dumps(ko_segments, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / f"{BASE}_korean_transcript.txt").write_text(
        "\n".join(f"[{fmt_txt(item['start'])}-{fmt_txt(item['end'])}] {item['text']}" for item in ko_segments),
        encoding="utf-8",
    )

    print(f"korean language={ko_info.language} prob={ko_info.language_probability:.3f} cues={len(ko_segments)}", flush=True)

    en_info, en_segments = transcribe(model, "translate")

    (OUT_DIR / f"{BASE}_english_translation.json").write_text(
        json.dumps(en_segments, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (OUT_DIR / f"{BASE}_english_translation.txt").write_text(
        "\n".join(f"[{fmt_txt(item['start'])}-{fmt_txt(item['end'])}] {item['text']}" for item in en_segments),
        encoding="utf-8",
    )

    srt_blocks = []
    for index, item in enumerate(en_segments, 1):
        srt_blocks.append(
            f"{index}\n{fmt_srt(item['start'])} --> {fmt_srt(item['end'])}\n{wrap_caption(item['text'])}"
        )
    (OUT_DIR / f"{BASE}_english.srt").write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")

    print(f"english language={en_info.language} prob={en_info.language_probability:.3f} cues={len(en_segments)}")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
