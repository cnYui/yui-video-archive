# -*- coding: utf-8 -*-
"""截 claude.dev 官方教程页最底部的太空场景（footer .scene）：深色模式，viewport 1440 宽，设备像素比 DSF（默认 4），连截几帧（宇航员会飘动）。

  python capture_scene.py [DSF]  → _src/scene/s{DSF}_{0..3}.png，并把 canvas 尺寸等信息打印出来
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "_src" / "scene"
URL = "https://claude.dev/blog/getting-started-with-claude-code-mods/"
DSF = float(sys.argv[1]) if len(sys.argv) > 1 else 4

with sync_playwright() as pw:
    b = pw.chromium.launch()
    ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=DSF, color_scheme="dark")
    pg = ctx.new_page()
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    info = pg.evaluate("""() => {
      const s = document.querySelector('footer .scene');
      if (!s) return null;
      const r = s.getBoundingClientRect();
      return {rect: [r.x, r.y + scrollY, r.width, r.height],
              canvases: [...s.querySelectorAll('canvas')].map(c => ({w: c.width, h: c.height, cw: c.clientWidth, ch: c.clientHeight, cls: c.className})),
              html: s.outerHTML.slice(0, 600)};
    }""")
    print(info)
    pg.evaluate("document.querySelector('footer .scene').scrollIntoView({block:'center'})")
    pg.wait_for_timeout(1500)
    sc = pg.query_selector("footer .scene")
    for i in range(4):
        pg.wait_for_timeout(700)
        sc.screenshot(path=str(OUT / f"s{int(DSF)}_{i}.png"))
        print("->", f"s{int(DSF)}_{i}.png")
    b.close()
