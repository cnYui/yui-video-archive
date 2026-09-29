# -*- coding: utf-8 -*-
"""逐句复核：large-v3-turbo（本机缓存）逐段听写 配音/segments/<段号>.wav，和台本的 TTS 文本比对。
分数只比汉字和字母（数字、标点、空格都去掉，中文数字也换成阿拉伯数字再比），列出分数低的段和原文、听写。
输出 check_segments.tsv。"""
import csv
import sys
import difflib
import json
import re
from pathlib import Path

from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
EP = HERE.parent.parent
segs = json.loads((EP / "台本" / "配音分段.json").read_text(encoding="utf-8"))
m = WhisperModel("mobiuslabsgmbh/faster-whisper-large-v3-turbo", device="cpu", compute_type="int8",
                 cpu_threads=12, local_files_only=True)

CN = {"零": "0", "一": "1", "二": "2", "两": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}


def norm(t):
    t = t.lower()
    t = re.sub(r"[^\w一-鿿]", "", t)       # drop punctuation / spaces
    t = re.sub(r"[0-9十百千万亿点零一二两三四五六七八九]", "", t)   # numbers are written differently; drop them
    return t


rows = []
for s in segs:
    wav = EP / "配音" / "segments" / f"{s['id']}.wav"
    out, _ = m.transcribe(str(wav), language="zh", beam_size=5, vad_filter=False,
                          initial_prompt="鲸鱼娘锐评大模型：夯、顶级、人上人、NPC、拉完了。")
    heard = "".join(x.text for x in out).strip()
    a, b = norm(s["tts_text"]), norm(heard)
    score = difflib.SequenceMatcher(None, a, b).ratio() if a else 1.0
    rows.append((s["id"], round(score, 3), s["tts_text"], heard))
    print(f"{s['id']} {score:.3f} | {heard}", flush=True)

TAG = sys.argv[1] if len(sys.argv) > 1 else ""
with open(HERE / f"check_segments{TAG}.tsv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t")
    w.writerow(["段号", "分数", "TTS 文本", "听写"])
    w.writerows(rows)
print(f"-> check_segments{TAG}.tsv")
