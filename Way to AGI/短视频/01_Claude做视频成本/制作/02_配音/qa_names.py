# -*- coding: utf-8 -*-
"""专名读音检查：用英文识别器（language="en"）逐句听含英文专名的几句，读歪的话会听成另一个词。"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
HERE = Path(__file__).resolve().parent
td = json.loads((HERE / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
wav = HERE / "edit" / "tts_narration.wav"
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32)
want = sys.argv[1:] or ["N01", "N02", "N03", "N07", "N09", "N13"]
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
for x in td["lines"]:
    if x["id"] not in want: continue
    seg = a[int(max(0, x["s"] - 0.1) * 16000): int((x["e"] + 0.15) * 16000)]
    segs, _ = m.transcribe(seg, language="en", initial_prompt="Google Veo 3.1, Claude, Opus 5.5, ffmpeg, JoJo, HTML, skill, Gintama, Naruto.", beam_size=5)
    print(x["id"], "|", " ".join(s.text.strip() for s in segs))
