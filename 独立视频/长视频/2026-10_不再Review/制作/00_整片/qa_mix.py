# -*- coding: utf-8 -*-
"""混音复核：把 audio/voice_only.wav（只有配音，和 mix.wav 同一时间轴、同一增益）按每条字幕的时间切出来单独识别（不带提示词），和字幕比；低于 0.8 的列出来。
另有 --mix：用整片混音 mix.wav 核（同传段里有原声垫底，分数会略低，用来确认“放对位置、没叠音”）。

  python qa_mix.py                 逐条核对（画外音 + 访谈里的中文同传）
  python qa_mix.py --dub           只核同传
  python qa_mix.py --mix           用 mix.wav 核
  python qa_mix.py --at 76 [其他.wav]   只识别某一时刻前后 6 s（对比新旧混音用）

2026-10-01 加：第一次投稿的版本配音块放错了位置（build_timeline.py 的 at 漏了 + b0），1:14–1:36 叠了四个声音，
当时只测了响度、看了画面，没有逐句听。以后出片前都跑一遍这个。
"""
import difflib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
n = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))


def load16(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16)


def asr(m, a, t0, t1):
    seg = a[int(max(0, t0) * 16000): int(t1 * 16000)]
    p = HERE / "audio" / "_qa.wav"
    with wave.open(str(p), "wb") as o:
        o.setnchannels(1)
        o.setsampwidth(2)
        o.setframerate(16000)
        o.writeframes(seg.tobytes())
    segs, _ = m.transcribe(str(p), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0)
    return "".join(s.text for s in segs)


def main():
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    if "--at" in sys.argv:
        i = sys.argv.index("--at")
        t = float(sys.argv[i + 1])
        src = Path(sys.argv[i + 2]) if len(sys.argv) > i + 2 else HERE / "audio" / "mix.wav"
        print(f"{src.name} @ {t - 3:.1f}–{t + 3:.1f}: {asr(m, load16(src), t - 3, t + 3)}")
        return
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    wav = HERE / "audio" / ("mix.wav" if "--mix" in sys.argv else "voice_only.wav")
    a = load16(wav)
    low = []
    only_dub = "--dub" in sys.argv
    for q in T["cues"]:
        if only_dub and q.get("kind") != "dub":
            continue
        hyp = asr(m, a, q["s"] - 0.15, q["e"] + 0.15)
        sc = difflib.SequenceMatcher(None, n(q["zh"]), n(hyp)).ratio()
        flag = "" if sc >= 0.8 else "  <<<"
        if sc < 0.8:
            low.append(q["id"])
        print(f"{q['id']} {q['s']:7.2f} {sc:.2f} {hyp}{flag}", flush=True)
    print(f"[{wav.name}] 共 {len(T['cues'])} 条，低于 0.8 的 {len(low)} 条：{' '.join(low) or '无'}")


if __name__ == "__main__":
    main()
