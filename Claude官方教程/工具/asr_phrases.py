# -*- coding: utf-8 -*-
r"""把 asr_own_voice.py 出的逐词 asr.json 按“气口”（相邻词间隔 ≥ GAP 秒）切成短语，打印 起 / 止 / 间隔 / 文字（低置信度的词加 ⟨⟩）。
剪口播时用它找句子边界和多余的停顿。

  python asr_phrases.py <ASR 目录>\<片段名> [GAP=0.25]
"""
import json
import sys
from pathlib import Path

d = Path(sys.argv[1])
gap = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25
rows = json.loads((d / "asr.json").read_text(encoding="utf-8"))
words = [w for r in rows for w in r["words"]]
groups, cur = [], [words[0]]
for a, b in zip(words, words[1:]):
    if b["s"] - a["e"] >= gap:
        groups.append(cur)
        cur = []
    cur.append(b)
groups.append(cur)
prev_e = 0.0
for g in groups:
    s, e = g[0]["s"], g[-1]["e"]
    txt = "".join(f"⟨{w['w']}⟩" if w["p"] < 0.5 else w["w"] for w in g)
    print(f"{s:7.2f} {e:7.2f}  gap {s - prev_e:4.2f}  {txt}")
    prev_e = e
