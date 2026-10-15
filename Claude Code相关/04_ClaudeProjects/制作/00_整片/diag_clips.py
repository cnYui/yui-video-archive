# -*- coding: utf-8 -*-
"""build_timeline 之后看一眼：每个素材场景 = 场景长度 / 真实播放的素材秒数 / 末尾定格了多少秒；页面 / A 版式场景只列长度。
定格太长（> 6 s）的场景，回 台本\\script_v2.py 里给它多配一段素材（别超出讲师没露脸的安全区间）或拆句。"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
tot_freeze = 0.0
for s in T["segs"]:
    c = T["clips"][s["id"]]
    d = s["e"] - s["s"]
    if c["ranges"]:
        play = sum(r["e"] - r["s"] for r in c["ranges"] if not r["hold"])
        frozen = sum(r["e"] - r["s"] for r in c["ranges"] if r["hold"])
        tot_freeze += frozen
        flag = "  ← 定格偏长" if frozen > 6 else ""
        print(f"{s['id']:4s} {s['layout']}  场景 {d:6.1f} s  播放 {play:5.1f} s  定格 {frozen:5.1f} s{flag}   {s['title']}")
    else:
        print(f"{s['id']:4s} {s['layout']}  场景 {d:6.1f} s  （{'A 版式要点' if s['layout'] == 'A' else '页面镜头'}）   {s['title']}")
print(f"整片 {T['total']:.1f} s；素材场景里定格合计 {tot_freeze:.1f} s")
