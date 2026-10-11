# -*- coding: utf-8 -*-
"""混音复核：把 out/<ep>/audio/mix.wav 按每条字幕的时间切出来单独识别（不带提示词），和字幕比；低于 0.8 的列出来。

  python qa_mix.py V1                 逐条核对（画外音 + 发布会片段里的中文同传）
  python qa_mix.py V1 --dub           只核同传
  python qa_mix.py V1 --at 76 [其他.wav]   只识别某一时刻前后 6 s（对比新旧混音用）

出片前都跑一遍（2026-10-01 的教训：第一次投稿的版本配音块放错了位置、叠了声音，当时只测了响度、看了画面，没有逐句听）。
识别用 whisper large-v3-turbo，曼波声线的 d/z、sh/x 音常被听成别的字，分数低不一定是真有问题：低分的再用逐词时间 / 单句识别核一遍。
"""
import difflib
import json
import re
import subprocess
import sys
import wave

import numpy as np
from faster_whisper import WhisperModel

from common import out_dir

n = lambda s: re.sub(r"[^\w]|_", "", s.lower().replace(" ", ""))


def load16(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.int16)


def asr(m, a, t0, t1, tmp):
    seg = a[int(max(0, t0) * 16000): int(t1 * 16000)]
    with wave.open(str(tmp), "wb") as o:
        o.setnchannels(1)
        o.setsampwidth(2)
        o.setframerate(16000)
        o.writeframes(seg.tobytes())
    segs, _ = m.transcribe(str(tmp), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0)
    return "".join(s.text for s in segs)


def main():
    ep = sys.argv[1]
    od = out_dir(ep)
    (od / "audio").mkdir(exist_ok=True)
    tmp = od / "audio" / "_qa.wav"
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    if "--at" in sys.argv:
        i = sys.argv.index("--at")
        t = float(sys.argv[i + 1])
        src = sys.argv[i + 2] if len(sys.argv) > i + 2 else od / "audio" / "mix.wav"
        print(f"{src} @ {t - 3:.1f}–{t + 3:.1f}: {asr(m, load16(src), t - 3, t + 3, tmp)}")
        return
    T = json.loads((od / "timeline.json").read_text(encoding="utf-8"))
    a = load16(od / "audio" / "mix.wav")
    low = []
    only_dub = "--dub" in sys.argv
    for q in T["cues"]:
        if only_dub and q.get("kind") != "clip":
            continue
        hyp = asr(m, a, q["s"] - 0.15, q["e"] + 0.15, tmp)
        sc = difflib.SequenceMatcher(None, n(q["zh"]), n(hyp)).ratio()
        flag = "" if sc >= 0.8 else "  <<<"
        if sc < 0.8:
            low.append(q["id"])
        print(f"{q['id']} {q['s']:7.2f} {sc:.2f} {hyp}{flag}", flush=True)
    print(f"{ep} 共 {len(T['cues'])} 条，低于 0.8 的 {len(low)} 条：{' '.join(low) or '无'}")


if __name__ == "__main__":
    main()
