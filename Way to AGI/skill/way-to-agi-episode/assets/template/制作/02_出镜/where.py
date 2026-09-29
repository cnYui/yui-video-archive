# -*- coding: utf-8 -*-
"""成片里的某一秒 → 原录像编号和秒数（查剪辑点用）。  python where.py 150.6 151.5"""
import json, sys
from pathlib import Path
d = json.loads((Path(__file__).resolve().parent / "edit" / "edit.json").read_text(encoding="utf-8"))
for a in sys.argv[1:]:
    t = float(a)
    for g in d["segments"]:
        L = g["src_e"] - g["src_s"]
        if g["out_s"] <= t < g["out_s"] + L + g["gap"]:
            src = g["src_s"] + (t - g["out_s"])
            print(f"{t:8.2f} → {g['clip']} @ {src:.2f}s" + ("（插入的停顿里）" if t >= g["out_s"] + L else ""))
            break
