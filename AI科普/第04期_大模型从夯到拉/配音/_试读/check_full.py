# -*- coding: utf-8 -*-
"""整期配音复核：large-v3-turbo（本机缓存，不下载）带词级时间戳听写 C01_v1.mp3，
输出 check_full.json（词）和 check_full.txt（带时间的句子），再找出几个关键词附近的原文。"""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
EP = HERE.parent.parent
audio = EP / "配音" / "raw" / (sys.argv[1] if len(sys.argv) > 1 else "C01_v1.mp3")
m = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8",
                 cpu_threads=12, local_files_only=True)
segs, info = m.transcribe(str(audio), language="zh", word_timestamps=True, beam_size=5, vad_filter=True,
                          initial_prompt="鲸鱼娘锐评大模型，从夯到拉：夯、顶级、人上人、NPC、拉完了。")
rows, words = [], []
for s in segs:
    rows.append(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}")
    words += [dict(w=w.word, s=round(w.start, 2), e=round(w.end, 2)) for w in (s.words or [])]
stem = audio.stem
(HERE / f"check_{stem}.txt").write_text("\n".join(rows), encoding="utf-8")
(HERE / f"check_{stem}.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
print(f"{len(rows)} 句，{info.duration:.1f}s -> check_{stem}.txt")
