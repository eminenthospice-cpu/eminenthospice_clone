import json
import subprocess
import sys
from pathlib import Path

PKG_FAST = Path(r"C:\Users\emine\AppData\Local\Temp\codex_audio_pkgs")
PKG_FFMPEG = Path(r"C:\Users\emine\AppData\Local\Temp\codex_ffmpeg_pkg")
sys.path.insert(0, str(PKG_FAST))
sys.path.insert(0, str(PKG_FFMPEG))

import imageio_ffmpeg
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel


ROOT = Path(r"C:\Users\emine\OneDrive\Desktop\Website_Clone")
VIDEO = Path(r"C:\Users\emine\Downloads\YTDown_YouTube_Media_edmwae3Iglk_001_1080p (1).mp4")
WAV = ROOT / "transcribe_audio_16k.wav"
OUT_JSON = ROOT / "transcribe_segments.json"
OUT_TXT = ROOT / "transcribe_raw.txt"

GLOSSARY = """
Eminent Hospice Care, 김정아, hospice, POLST, Physician Orders for Life-Sustaining Treatment,
CPR, DNR, advance directive, Medicare, Medi-Cal, RN, LVN, nurse practitioner, chaplain,
bereavement care, morphine, lorazepam, atropine, acetaminophen, Dulcolax, nebulizer,
oxygen concentrator, nasal cannula, suction machine, suction catheter, nasogastric tube, feeding tube
"""


def ts(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def group_words(segments, target_seconds=8.0):
    groups = []
    cur_words = []
    start = None
    last_end = None

    for seg in segments:
        words = list(seg.words or [])
        if not words:
            groups.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
            continue
        for word in words:
            if start is None:
                start = word.start
            cur_words.append(word.word)
            last_end = word.end
            if last_end - start >= target_seconds:
                groups.append({"start": start, "end": last_end, "text": "".join(cur_words).strip()})
                cur_words = []
                start = None
                last_end = None

    if cur_words:
        groups.append({"start": start or 0.0, "end": last_end or start or 0.0, "text": "".join(cur_words).strip()})
    return groups


def main():
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(VIDEO),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            str(WAV),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    audio, sr = sf.read(str(WAV), dtype="float32")
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    model = WhisperModel("medium", device="cpu", compute_type="int8", download_root=str(ROOT / ".whisper_models"))
    segments_iter, info = model.transcribe(
        audio,
        language="ko",
        task="transcribe",
        beam_size=5,
        best_of=5,
        temperature=0,
        condition_on_previous_text=True,
        word_timestamps=True,
        initial_prompt=GLOSSARY,
        vad_filter=False,
    )
    segments = list(segments_iter)
    groups = group_words(segments)

    serializable = [
        {
            "start": g["start"],
            "end": g["end"],
            "timestamp": ts(g["start"]),
            "text": g["text"],
        }
        for g in groups
    ]
    OUT_JSON.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_TXT.write_text("\n".join(f"[{item['timestamp']}] {item['text']}" for item in serializable), encoding="utf-8")
    (ROOT / "transcribe_model_segments.txt").write_text(
        "\n".join(f"[{ts(s.start)}-{ts(s.end)}] {s.text.strip()}" for s in segments),
        encoding="utf-8",
    )
    print(f"language={info.language} prob={info.language_probability:.3f} duration={len(audio)/sr:.2f}")
    print(str(OUT_TXT))


if __name__ == "__main__":
    main()
