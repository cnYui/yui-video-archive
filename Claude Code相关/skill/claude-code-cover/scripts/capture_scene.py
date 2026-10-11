# -*- coding: utf-8 -*-
"""截 claude.dev 官方教程页最底部的太空场景（`footer .scene`）：深色模式、viewport 1440 宽、设备像素比 6，连截 4 帧
（宇航员会飘动，每帧的姿势和小星光都不一样）。

  python capture_scene.py [--url URL] [--dsf 6] [--frames 4] [--out ../assets/scene_src]

→ s6_0.png … s6_3.png（8550×4056，每张约 400 KB）。之后跑 build_assets.py 抠宇航员。
只在官方改了这幅插画、或找不到 `footer .scene` 时才需要重跑；assets/scene_src 里已经有 2026-10-02 截的一套。
场景结构（2026-10-02）：`.scene` 里一张 2 倍分辨率的星空 <canvas>（灰色点阵的月牙、土星、星点）+ `.astro-stage` 里的 DOM 像素宇航员
（身体 #D97757，头盔浅灰线，黄色小星光）。宇航员是 DOM 元素，设备像素比 6 下依然清晰；星空只有 2 倍，被放大了。
"""
import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
URL = "https://claude.dev/blog/getting-started-with-claude-code-mods/"

ap = argparse.ArgumentParser()
ap.add_argument("--url", default=URL)
ap.add_argument("--dsf", type=float, default=6)
ap.add_argument("--frames", type=int, default=4)
ap.add_argument("--out", default=str(HERE.parent / "assets" / "scene_src"))
a = ap.parse_args()
out = Path(a.out)
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=a.dsf, color_scheme="dark")
    pg = ctx.new_page()
    pg.goto(a.url, wait_until="networkidle", timeout=60000)
    info = pg.evaluate("""() => {
      const s = document.querySelector('footer .scene');
      if (!s) return null;
      const r = s.getBoundingClientRect();
      return {size: [r.width, r.height],
              canvases: [...s.querySelectorAll('canvas')].map(c => [c.width, c.height]),
              bg: getComputedStyle(document.body).backgroundColor, text: getComputedStyle(document.body).color};
    }""")
    if not info:
        raise SystemExit("找不到 footer .scene：官方页面改版了，去看看页面底部现在是什么，改这里的选择器")
    print(info)
    pg.evaluate("document.querySelector('footer .scene').scrollIntoView({block:'center'})")
    pg.wait_for_timeout(1500)
    sc = pg.query_selector("footer .scene")
    for i in range(a.frames):
        pg.wait_for_timeout(700)
        sc.screenshot(path=str(out / f"s{int(a.dsf)}_{i}.png"))
        print("->", out / f"s{int(a.dsf)}_{i}.png")
    b.close()
