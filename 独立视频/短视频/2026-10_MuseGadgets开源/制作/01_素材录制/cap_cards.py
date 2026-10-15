# -*- coding: utf-8 -*-
"""录官网首页「Project Ideas」轮播的 8 张卡片（2× 像素），存成 cards/card_N.png + cards.json。
轮播 = DIV.exampleTrackViewport（overflow hidden + 右缘遮罩）里的 UL.exampleTrack（横向滚动、滚动吸附）。
做法：关掉吸附和遮罩，把 UL 滚到每张卡片的左边，再按卡片的矩形截视口（真实页面内容）；滚动动画在 make_cards_clip.py 里离线做。"""
import io
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

OUT = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库\cards")
OUT.mkdir(parents=True, exist_ok=True)
UL = "ul[class*=exampleTrack]"
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 800, "height": 900}, device_scale_factor=2, locale="en-US")
    pg = ctx.new_page()
    pg.goto("https://gadgets.muse.ai/", wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(2500)
    H = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < H:                                   # 滚一遍触发图片懒加载
        pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(250); y += 600
    pg.wait_for_timeout(1200)
    pg.evaluate("""(sel) => {
      const ul = document.querySelector(sel);
      ul.style.scrollSnapType = 'none';
      for (let e = ul; e && e !== document.documentElement; e = e.parentElement) { e.style.maskImage = 'none'; e.style.webkitMaskImage = 'none'; }
      for (const e of ul.querySelectorAll('*')) { e.style.maskImage = 'none'; e.style.webkitMaskImage = 'none'; }
      ul.scrollIntoView({block: 'center'});
    }""", UL)
    pg.wait_for_timeout(600)
    n = pg.evaluate("(sel) => document.querySelector(sel).children.length", UL)
    cards = []
    for i in range(n):
        pg.evaluate("([sel, i]) => { const ul = document.querySelector(sel); const li = ul.children[i]; ul.scrollLeft = li.offsetLeft - ul.offsetLeft; }", [UL, i])
        pg.wait_for_timeout(700)
        box = pg.evaluate("([sel, i]) => { const li = document.querySelector(sel).children[i]; const r = li.getBoundingClientRect(); return {x: r.x, y: r.y, w: r.width, h: r.height, t: li.innerText}; }", [UL, i])
        png = pg.screenshot(clip={"x": box["x"], "y": box["y"], "width": box["w"], "height": box["h"]})
        f = OUT / f"card_{i}.png"
        f.write_bytes(png)
        im = Image.open(io.BytesIO(png))
        text = " | ".join(x.strip() for x in box["t"].splitlines() if x.strip())
        cards.append({"i": i, "file": f.name, "size": im.size, "text": text})
        print(i, im.size, text[:100])
    bg = pg.evaluate("() => getComputedStyle(document.body).backgroundColor")
    (OUT / "cards.json").write_text(json.dumps({"bg": bg, "cards": cards}, ensure_ascii=False, indent=1), encoding="utf-8")
    ctx.close(); b.close()
