# -*- coding: utf-8 -*-
"""对 PBS 视频里选中的几处做词级精转（large-v3-turbo，beam 5，词级时间戳），一次加载模型。
输出 素材/现场视频/转写/ranges.json：{名字: [{w, s, e}, …]}（时间是视频里的秒）和 ranges.txt（每词带时间，方便定入出点）。
"""
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
LIVE = HERE.parent / "素材" / "现场视频"
SRC = LIVE / "pbs_1XVhpiRSHv8.mp4"
RANGES = {                       # 名字: (起, 止) 秒
    "A_bound": (49.0, 63.0),     # 问“有没有约束力” → “道德上有约束力”
    "B_const": (104.0, 118.0),   # “宪法”那句
    "C_cmte": (145.0, 160.0),    # 约十人的委员会
    "D_dario": (1196.0, 1252.0), # 阿莫迪
    "E_mark": (1312.0, 1356.0),  # 扎克伯格
}
PROMPT = ("White House Accord on Super Intelligence. President Trump, Dario Amodei of Anthropic, Mark Zuckerberg of Meta, "
          "self-policing, morally binding, constitution, committee, internal controls, external auditors and evaluators, boards of directors.")


def main():
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=6)
    out, txt = {}, []
    for name, (a, b) in RANGES.items():
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "a.wav"
            subprocess.run([ffmpeg, "-y", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", str(SRC), "-vn", "-ac", "1", "-ar", "16000",
                            "-c:a", "pcm_s16le", str(wav)], check=True)
            segs, info = model.transcribe(str(wav), language="en", beam_size=5, initial_prompt=PROMPT, condition_on_previous_text=False,
                                          vad_filter=False, word_timestamps=True)
            words = []
            for s in segs:
                for w in (s.words or []):
                    words.append({"w": w.word, "s": round(w.start + a, 2), "e": round(w.end + a, 2)})
        out[name] = words
        txt.append(f"=== {name} ({a:.0f}–{b:.0f})\n" + " ".join(f"{w['w'].strip()}@{w['s']:.2f}" for w in words) + "\n")
        print(name, len(words), "词", flush=True)
    (LIVE / "转写" / "ranges.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (LIVE / "转写" / "ranges.txt").write_text("\n".join(txt), encoding="utf-8")


if __name__ == "__main__":
    main()
