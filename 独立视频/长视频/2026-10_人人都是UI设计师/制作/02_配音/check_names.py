# -*- coding: utf-8 -*-
"""带英文专名的句子用英文识别器听一遍（不带提示词）：看专名有没有读歪。中文识别器会把英文词写成音近的中文 / 拼音，分数不可信。

  python check_names.py [句号 …]     默认：A05 A06 A07 R04b R12d R14b R19c Z06 Z09

输出每句的英文识别结果（中文部分会被写成拼音式的乱码，不用管，只看英文专名）。
"""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
ids = sys.argv[1:] or ["A05", "A06", "A07", "R04b", "R12d", "R14b", "R19c", "R19e", "Z06", "Z09"]
lines = json.loads((HERE.parents[1] / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
idx = {l["id"]: i for i, l in enumerate(lines)}
files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
model = WhisperModel("small", device="cpu", compute_type="int8")
for i in ids:
    p = HERE / "tts" / "seg_pick_v3" / f"{i}.wav"
    p = p if p.exists() else files[idx[i]]
    segs, _ = model.transcribe(str(p), language="en", beam_size=5, condition_on_previous_text=False)
    print(i, "|", lines[idx[i]]["say"], "→", " ".join(s.text.strip() for s in segs))
