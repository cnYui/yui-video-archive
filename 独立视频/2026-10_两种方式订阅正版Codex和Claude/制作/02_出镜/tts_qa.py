# -*- coding: utf-8 -*-
"""逐句复核拼好的克隆配音：每句单独切出来识别（不带提示词），和原文比；分数低的列出来。  python tts_qa.py"""
import json, re, difflib, subprocess, wave
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
n = lambda s: re.sub(r"[^\w]|_", "", s.lower())
d = json.loads((HERE / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
lines = {l["id"]: l for l in json.loads((HERE / "tts" / "lines.json").read_text(encoding="utf-8"))}
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
with wave.open(str(HERE / "edit" / "tts_narration.wav")) as w:
    sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).mean(1).astype(np.int16)
bad = 0
for x in d["lines"]:
    seg = a[int(max(0, x["s"] - 0.15) * sr): int((x["e"] + 0.15) * sr)]
    with wave.open(str(HERE / "tts" / "_q.wav"), "wb") as o:
        o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr); o.writeframes(seg.tobytes())
    segs, _ = m.transcribe(str(HERE / "tts" / "_q.wav"), language="zh", beam_size=5, condition_on_previous_text=False, temperature=0)
    hyp = "".join(s.text for s in segs)
    sc = difflib.SequenceMatcher(None, n(lines[x["id"]]["say"]), n(hyp)).ratio()
    flag = "" if sc >= 0.85 else "  <<<"
    bad += sc < 0.85
    print(f"{x['id']} {sc:.2f} {hyp}{flag}")
print("低于 0.85 的：", bad)
