# -*- coding: utf-8 -*-
"""第二意见：本机缓存的 medium + 简体 / 专名提示词，逐句和 say 对比；和 large-v3-turbo 都低的才算问题。"""
import json, re, subprocess
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
sc = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
td = json.loads((HERE / "edit" / "tts_edit.json").read_text(encoding="utf-8"))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HERE / "edit" / "tts_narration.wav"), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32)
m = WhisperModel("medium", device="cpu", compute_type="int8")
import difflib
def norm(s): return re.sub(r"[^\w\u4e00-\u9fff]", "", s).lower()
say = {l["id"]: l["zh"] for l in sc["lines"]}
for x in td["lines"]:
    seg = a[int(max(0, x["s"] - 0.1) * 16000): int((x["e"] + 0.15) * 16000)]
    segs, _ = m.transcribe(seg, language="zh", initial_prompt="以下是普通话的句子，使用简体中文。内容有 Claude、Opus 5.5、Google Veo 3.1、ffmpeg、JoJo、HTML、skill、悠一。", beam_size=5)
    t = "".join(s.text for s in segs)
    r = difflib.SequenceMatcher(None, norm(say[x["id"]]), norm(t)).ratio()
    print(f'{x["id"]} {r:.2f} {t}' + ("  <<<" if r < 0.85 else ""))
