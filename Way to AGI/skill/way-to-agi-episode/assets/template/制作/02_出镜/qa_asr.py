# -*- coding: utf-8 -*-
"""剪好的口播再识别一遍（查剪辑点有没有漏掉口癖、切掉半个字）：edit/narration.wav → edit/_qa_asr.txt / .json。"""
import json
import subprocess
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
E = HERE / "edit"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(E / "narration.wav"), "-ac", "1", "-ar", "16000", str(E / "narration16.wav")], check=True)
model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
segs, _ = model.transcribe(str(E / "narration16.wav"), language="zh", beam_size=5, word_timestamps=True,
                           initial_prompt="嗯，那个，就是说。Claude Opus 5.5，GPT-6，ffmpeg，HTML，BGM，LLM，扩散模型，悠一。",
                           condition_on_previous_text=False, vad_filter=False)
out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word, "s": round(w.start, 2), "e": round(w.end, 2)} for w in (s.words or [])]})
(E / "_qa_asr.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
(E / "_qa_asr.txt").write_text("".join(f"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text']}\n" for s in out), encoding="utf-8")
print(len(out), "segments")
