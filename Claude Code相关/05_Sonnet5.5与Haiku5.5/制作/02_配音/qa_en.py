# -*- coding: utf-8 -*-
"""英文专名听读：把含英文词的句子用英文识别器（language="en"）单独听一遍，看专名有没有被读成别的词。
中文部分识别出来是乱的，不用管；只看 Anthropic / Opus / Sonnet / Haiku / Fable / Luna / Claude Code / Max / Team / token / API /
Terminal Bench / OS World / G D P val A A / Chartography / X high 这些词有没有出现、听成了什么。
  python qa_en.py            → qa_en.txt
输入：tts/seg_raw/final/NNNNNN.wav（顺序 = 台本 lines），tts/lines.json。
"""
import json
import re
import sys
import wave
from pathlib import Path

import numpy as np
import subprocess

HERE = Path(__file__).resolve().parent
WORDS = ["Anthropic", "Opus", "Sonnet", "Haiku", "Fable", "Luna", "Claude", "Code", "Max", "Team", "token", "API",
         "Terminal", "Bench", "OS", "World", "Chartography", "high", "GPT"]


def load16k(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def main():
    from faster_whisper import WhisperModel
    lines = json.loads((HERE / "tts" / "lines.json").read_text(encoding="utf-8"))
    files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
    assert len(files) == len(lines)
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=6)
    out = []
    only = set(sys.argv[1:])                       # 只听指定的几句：python qa_en.py N49 N51 …（CPU 上每句约 30 s）
    for l, f in zip(lines, files):
        if only and l["id"] not in only:
            continue
        want =[w for w in WORDS if re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![a-z])", l["say"] + " " + l["zh"], re.I)]
        if not want:
            continue
        segs, _ = m.transcribe(load16k(f), language="en", beam_size=5, condition_on_previous_text=False, temperature=0)
        hyp = " ".join(s.text.strip() for s in segs)
        miss = [w for w in want if not re.search(re.escape(w), hyp, re.I)]
        out.append(f"{l['id']:5s} 要听到：{' '.join(want)}\n      听成：{hyp}\n      没听到：{' '.join(miss) or '—'}")
        print(out[-1], flush=True)
    (HERE / "qa_en.txt").write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
