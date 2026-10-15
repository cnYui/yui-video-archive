# -*- coding: utf-8 -*-
"""录官网 Home Link 3D 小组件（https://gadgets.muse.ai/gadgets/home-link-widget/index.html，官网首页里嵌的 iframe）的高清静帧。
365×360 CSS 视口、2× 以上像素：Device（转台，连拍一段挑正面）/ What's inside / Connection（小圆点沿线跑，连拍一段）。
CDP captureScreenshot 带 clip.scale：每帧约 150 ms（6–7 fps），所以动画只当“步进”用。"""
import base64, json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库\widget")
OUT.mkdir(parents=True, exist_ok=True)
SCALE = 3
URL = "https://gadgets.muse.ai/gadgets/home-link-widget/index.html"


def shot(cdp, path):
    r = cdp.send("Page.captureScreenshot", {"format": "png", "optimizeForSpeed": True, "clip": {"x": 0, "y": 0, "width": 365, "height": 360, "scale": SCALE}})
    Path(path).write_bytes(base64.b64decode(r["data"]))
    return time.time()


with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 365, "height": 360}, device_scale_factor=1, locale="en-US")
    pg = ctx.new_page()
    pg.goto(URL, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(1200)
    cdp = ctx.new_cdp_session(pg)
    labels = pg.query_selector_all(".cadViewLabel")
    meta = {"scale": SCALE, "device": [], "inside": None, "connection": []}
    # Device：连拍 9 s
    t0 = time.time()
    n = 0
    while time.time() - t0 < 9:
        fn = OUT / f"device_{n:03d}.png"
        t = shot(cdp, fn)
        meta["device"].append([n, round(t - t0, 2)])
        n += 1
    # What's inside：点完等 2.5 s 稳定后拍 1 张
    labels[1].click()
    pg.wait_for_timeout(2500)
    shot(cdp, OUT / "inside.png")
    meta["inside"] = "inside.png"
    # Connection：点完等 1.2 s（转场），连拍 7 s
    labels[2].click()
    pg.wait_for_timeout(1200)
    t0 = time.time()
    n = 0
    while time.time() - t0 < 7:
        fn = OUT / f"connection_{n:03d}.png"
        t = shot(cdp, fn)
        meta["connection"].append([n, round(t - t0, 2)])
        n += 1
    (OUT / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    print("device frames", len(meta["device"]), "connection frames", len(meta["connection"]))
    ctx.close(); b.close()
