# -*- coding: utf-8 -*-
"""抽样核对字幕条和成片声音对得上：均匀挑 N 条字幕，把正片声音里这条的时间窗（字幕 s–e）切出来识别，和字幕文字比相似度。
时间窗里识别出来的话和字幕差很多 = 字幕时间 / 画面时间错位。python check_sync.py [N]"""
import json
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
cues = [c for c in T["cues"] if c["e"] - c["s"] >= 2.5]
step = max(1, len(cues) // N)
pick = cues[step // 2::step][:N]
model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=6)
tmp = HERE / "audio" / "_sync.wav"
bad = 0
for c in pick:
    s, e = c["s"], c["e"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s - 0.15:.3f}", "-t", f"{e - s + 0.3:.3f}", "-i", str(HERE / "整片_正片_v1.mp4"), "-vn", "-ac", "1", "-ar", "16000", str(tmp)], check=True)
    segs, _ = model.transcribe(str(tmp), language="zh", beam_size=3, condition_on_previous_text=False)
    heard = "".join(x.text for x in segs)

    def norm(x):
        return "".join(ch for ch in x if ch.isalnum()).lower()
    r = SequenceMatcher(None, norm(heard), norm(c["zh"])).ratio()
    flag = "" if r >= 0.45 else "   ← 对不上？"
    bad += r < 0.45
    print(f"{c['id']} {s:7.2f}–{e:7.2f}  相似 {r:.2f}{flag}\n   字幕：{c['zh'][:46]}\n   听到：{heard[:46]}")
print(f"抽查 {len(pick)} 条，疑似对不上 {bad} 条")
