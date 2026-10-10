# -*- coding: utf-8 -*-
"""复查识别（edit/_qa_asr.json）和字幕条逐条对照：找缺头、缺尾、多出来的字。
  python qa_check.py        → 每条字幕：原文开头 / 结尾两个字在复查识别里有没有（同音字也算对，按拼音比）"""
import json
import re
from pathlib import Path

from pypinyin import lazy_pinyin

HERE = Path(__file__).resolve().parent
ed = json.loads((HERE / "edit" / "edit.json").read_text(encoding="utf-8"))
qa = json.loads((HERE / "edit" / "_qa_asr.json").read_text(encoding="utf-8"))
words = [(w["s"], w["e"], w["w"].strip()) for s in qa for w in s["words"]]


def norm(t):
    t = re.sub(r"（[^）]*）", "", t)
    t = re.sub(r"[^\w]", "", t).lower()
    return t


def py(t):
    return [p for p in lazy_pinyin(t) if p.strip()]


bad = 0
for q in ed["cues"]:
    got = "".join(w for s, e, w in words if s >= q["out_s"] - 0.6 and e <= q["out_e"] + 0.6)
    want = norm(q["zh"])
    g = py(norm(got))
    w = py(want)
    head = w[:2]
    tail = w[-2:]
    ok_h = any(g[i:i + 2] == head for i in range(len(g)))
    ok_t = any(g[i:i + 2] == tail for i in range(len(g)))
    if not (ok_h and ok_t):
        bad += 1
        flag = ("缺头" if not ok_h else "") + ("缺尾" if not ok_t else "")
        print(f"{q['id']:5s} {q['out_s']:7.2f} {flag:4s} 原文：{q['zh']}\n{'':19s}识别：{got}")
print(f"{bad} 条可疑 / {len(ed['cues'])}")
