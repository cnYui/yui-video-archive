# -*- coding: utf-8 -*-
"""“夯”的读音复核（不给识别器任何提示词，免得它把 hēng 也写成“夯”）：
按 配音/segments/ 里当前的切句，听写含“夯”的几段，打印结果。用法：python check_hang.py [标签]"""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
EP = HERE.parent.parent
segs = json.loads((EP / "台本" / "配音分段.json").read_text(encoding="utf-8"))
ids = [s["id"] for s in segs if "夯" in s["tts_text"]]
m = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8",
                 cpu_threads=12, local_files_only=True)
tag = sys.argv[1] if len(sys.argv) > 1 else ""
lines = []
for sid in ids:
    out, _ = m.transcribe(str(EP / "配音" / "segments" / f"{sid}.wav"), language="zh", beam_size=5, vad_filter=False)
    heard = "".join(x.text for x in out).strip()
    ok = "夯" in heard
    lines.append(f"{tag} {sid} {'✓' if ok else '✗'} | {heard}")
    print(lines[-1], flush=True)
(HERE / f"check_hang{tag}.txt").write_text("\n".join(lines), encoding="utf-8")
