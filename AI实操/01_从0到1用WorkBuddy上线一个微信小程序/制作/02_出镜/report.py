# -*- coding: utf-8 -*-
"""看剪辑表：python report.py [段号…]  → 每个片段的类型、主时间、倍速、成片时间；字幕条在成片里的位置。
   python report.py --where 秒 [秒…]  → 成片里的这一秒来自哪一段的主时间多少（改剪辑点用）"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "edit" / "edit.json").read_text(encoding="utf-8"))
FPS = d["fps"]


def mmss(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


a = sys.argv[1:]
if a[:1] == ["--where"]:
    for x in a[1:]:
        f = float(x) * FPS
        for c in d["clips"]:
            if c["out0"] <= f < c["out0"] + c["n"]:
                m = c["m0"] + (f - c["out0"]) / FPS * c["speed"]
                print(f"{x}s → 段{c['seg']} {c['take']} 主时间 {m:.2f}s（{c['kind']}，×{c['speed']}）")
    sys.exit()
segs = [int(x) for x in a] if a else range(len(d["segs"]))
cue_by_seg = {}
for q in d["cues"]:
    cue_by_seg.setdefault(q["seg"], []).append(q)
for i in segs:
    s = d["segs"][i]
    print(f"\n══ 段 {i} {s['take']} 版式 {s['layout']} 第 {s['chapter']} 章")
    for c in d["clips"]:
        if c["seg"] != i:
            continue
        o = c["out0"] / FPS
        m1 = c["m0"] + c["n"] / FPS * c["speed"]
        aud = f"{c['aud'][0]}@{c['aud'][1]:.2f}" if c["aud"] else "静音"
        print(f"  {mmss(o):>9}  {c['kind']:6s} 主 {c['m0']:8.2f}–{m1:8.2f}  ×{c['speed']:<6} {c['n'] / FPS:5.2f}s  {aud:16s} {','.join(c['cues'])}")
    for q in cue_by_seg.get(i, []):
        print(f"     字幕 {q['id']:5s} {mmss(q['out_s'])}–{mmss(q['out_e'])}  {q['zh']}")
