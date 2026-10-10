# -*- coding: utf-8 -*-
"""剪好的人声再识别一遍（查漏掉的口癖、切掉半个字、重复的词）：edit/narration.wav → edit/_qa_asr.txt / .json。
提示词故意带口癖，口癖才会被写出来。时间是成片时间；用 report.py --where 秒 换算回原录像。"""
import json
import subprocess
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
E = HERE / "edit"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(E / "narration.wav"), "-ac", "1", "-ar", "16000", str(E / "narration16.wav")], check=True)
model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
segs, _ = model.transcribe(str(E / "narration16.wav"), language="zh", beam_size=5, word_timestamps=True,
                           initial_prompt="嗯，那个，就是说，呃，啊。WorkBuddy，微信开发者工具，CLI，CloudBase，AppID，悠一。",
                           condition_on_previous_text=False, vad_filter=True)
out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]})
(E / "_qa_asr.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
(E / "_qa_asr.txt").write_text("".join(f"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text']}\n" for s in out), encoding="utf-8")
print(len(out), "segments")
