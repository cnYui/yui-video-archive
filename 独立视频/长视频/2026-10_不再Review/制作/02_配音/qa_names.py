# -*- coding: utf-8 -*-
"""专名读音复核：这个声线（曼波）读英文专名会读歪（Tavus → Typhus、Griffin → Ruffin），温柔男生要重测。
对每一句含英文专名的配音（tts/seg_raw/final/NNNNNN.wav，一句一个文件，顺序 = 录制稿 lines），用 whisper 的**英文模式**（large-v3-turbo，不带提示词）识别，
把识别结果和台本里的专名对一下：专名没出现的列出来，用耳朵听这几句；读歪了就在 say 里换成中文音译、只重生成那几句。

  python qa_names.py
"""
import json
import re
import subprocess
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
NAMES = ["Lauren Tan", "poteto", "Matt Pocock", "SpaceXAI", "Grok Bot", "pstack", "Cursor", "autopilot", "Claude Max", "Review", "Token", "lint", "SEV", "PR", "AI"]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    lines = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
    files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
    assert len(files) == len(lines), (len(files), len(lines))
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8", cpu_threads=8)
    bad = []
    for l, f in zip(lines, files):
        want = [n for n in NAMES if n.lower() in l["say"].lower() and n not in ("PR", "AI", "Review")]
        if not want:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "a.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-ac", "1", "-ar", "16000", str(wav)], check=True)
            segs, _ = m.transcribe(str(wav), language="en", beam_size=5, condition_on_previous_text=False, temperature=0)
            hyp = " ".join(s.text.strip() for s in segs)
        miss = [n for n in want if norm(n) not in norm(hyp)]
        flag = f"  <<< 没认出：{', '.join(miss)}" if miss else ""
        if miss:
            bad.append(l["id"])
        print(f"{l['id']}  专名：{', '.join(want)}\n    识别：{hyp}{flag}", flush=True)
    print("专名没出现的句子：", " ".join(bad) or "无")


if __name__ == "__main__":
    main()
