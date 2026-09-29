# -*- coding: utf-8 -*-
"""白底版对比度扫描（第 4 期 2026-09-28，用法：python 制作/检查/contrast_sweep.py [间隔秒，默认 0.5]）：复用本期 engine/check_layout.py 的检查脚本，按固定间隔扫整段正片（章节标题缩角那几秒加密），
只汇总 low-contrast（以及 overflow / outside）这几类，按元素合并成时间段打印。
已知误报：`mchip:… text #141414 on #2A2926 (tbBody)` 只在名字卡落地前那一刻出现——飞行层设了 pointer-events: none，
elementsFromPoint 取不到飞行中的名字卡，算成了下面的榜单底色；实际画面上是纸白名字卡配深色字。
`tbLab sm:拉完了 … on #C4C2BD` 是章节标题居中、榜单压暗到 0.22 的那一瞬间（故意压暗）。"""
import importlib.util
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

EP = Path(__file__).resolve().parent.parent          # 本期的 制作/
spec = importlib.util.spec_from_file_location("cl", EP / "engine" / "check_layout.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)

data = json.loads((EP / "timeline.json").read_text(encoding="utf-8"))
dur = data["main_duration"]
step = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
ts = set(round(i * step, 2) for i in range(int(dur / step) + 1))
# 每章开头 0–8 s 加密到 0.1 s（标题居中 → 缩到左上角）
for sc in data["scenes"]:
    for k in range(81):
        t = round(sc["start"] + k * 0.1, 2)
        if t < dur:
            ts.add(t)
ts = sorted(ts)
KEEP = ("low-contrast", "overflow", "outside", "offscreen")
cw, ch = cl.canvas_of(data)
hits = {}
with sync_playwright() as p:
    b = p.chromium.launch(args=["--force-color-profile=srgb"])
    pg = b.new_page(viewport={"width": cw, "height": ch})
    pg.add_init_script(f"window.__CAPTURE__=true;window.__CANVAS__=[{cw},{ch}];window.__DATA__="
                       + json.dumps(data, ensure_ascii=False) + ";")
    pg.goto((EP / "engine" / "index.html").resolve().as_uri())
    pg.wait_for_function("window.__READY__ === true", timeout=30000)
    for t in ts:
        for r in pg.evaluate(cl.JS, t):
            if r.startswith(KEEP):
                key = r.split(":")[0] + ":" + r.split(":", 1)[1].split(" text ")[0].split(" [")[0]
                hits.setdefault(key, []).append((t, r))
    b.close()
print(f"{len(ts)} moments, step {step}s (+0.1s for 8s after each scene start)")
for key, lst in sorted(hits.items(), key=lambda kv: kv[1][0][0]):
    t0, t1 = lst[0][0], lst[-1][0]
    print(f"{len(lst):4d}x  t {t0:7.2f}–{t1:7.2f}  {lst[0][1]}")
print("done")
