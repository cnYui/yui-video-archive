# -*- coding: utf-8 -*-
"""两个配音版本逐句比：用 tts_build 的对齐拿每句在各版本里的 (起, 止)，再把这个范围里识别出来的字拼起来和台本比。
默认版本 v1；两版分数差 ≥ 0.05 才换。python pick_takes.py [--write]  → --write 把建议写进 edit/choice.json"""
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tts_build as tb  # noqa: E402

HERE = Path(tb.HERE)
lines = json.loads((HERE / "tts" / "lines.json").read_text(encoding="utf-8"))
n = lambda s: re.sub(r"[^\w]|_", "", s.lower()).replace("5", "五").replace("1", "一").replace("2", "二")
res = {}
for v in ("v1", "v2"):
    asr = json.loads((HERE / "asr" / f"N_{v}.json").read_text(encoding="utf-8"))
    spans = tb.align(lines, asr)
    words = [(w["s"], w["e"], w["w"]) for s in asr["segments"] for w in s["words"]]
    res[v] = []
    for i, l in enumerate(lines):
        sp = spans[i]
        hyp = "".join(w for s, e, w in words if sp and s >= sp[0] - 0.05 and e <= sp[1] + 0.05)
        sc = difflib.SequenceMatcher(None, n(l["say"]), n(hyp)).ratio()
        res[v].append((sc, hyp, sp))
choice = {}
for i, l in enumerate(lines):
    a, b = res["v1"][i], res["v2"][i]
    pick = "v2" if b[0] >= a[0] + 0.05 else "v1"
    choice[l["id"]] = pick
    print(f"{l['id']} v1 {a[0]:.2f}  v2 {b[0]:.2f}  → {pick}   {l['say']}\n        v1: {a[1]}  [{a[2][0]:.2f}-{a[2][1]:.2f}]\n        v2: {b[1]}  [{b[2][0]:.2f}-{b[2][1]:.2f}]")
if "--write" in sys.argv:
    (HERE / "edit").mkdir(exist_ok=True)
    (HERE / "edit" / "choice.json").write_text(json.dumps(choice, ensure_ascii=False), encoding="utf-8")
    print("choice.json 已写：", choice)
