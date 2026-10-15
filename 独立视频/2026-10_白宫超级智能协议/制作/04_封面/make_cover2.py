# -*- coding: utf-8 -*-
"""封面 v2（用户 2026-10-01 要求）：背景用川普开会的现场画面（白宫官方视频，美国政府作品），
加《超级智能协定》，标题：一个视频带你看懂：昨天川普和6位CEO到底签署了啥？

  python make_cover2.py → 封面_C_16x9.png / 封面_C_4x3.png（会议桌全景）、封面_D_*（近景）；封面_选定_* = C

背景帧：wh_official_6UBA8iL3x54.mp4 第 64 s（会议桌全景）、第 112 s（近景，正脸、睁眼）；裁掉下面的白宫“TEXT POTUS”字幕条。
"""
import base64
import io
import shutil
import subprocess
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
VID = HERE.parents[1] / "素材" / "现场视频" / "wh_official_6UBA8iL3x54.mp4"
BG = HERE / "_bg"
BG.mkdir(exist_ok=True)


def frame(t):
    f = BG / f"wh_{t:06.1f}.png"
    if not f.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(VID), "-frames:v", "1", str(f)], check=True)
    return Image.open(f).convert("RGB")


def data_uri(im):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=94)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def crop(im, cx, h, w_out, h_out):
    """以 cx 为中心、高 h（从顶往下）、宽按输出比例切一块再缩放。"""
    w = int(h * w_out / h_out)
    x0 = min(max(0, int(cx - w / 2)), im.width - w)
    return im.crop((x0, 0, x0 + w, h)).resize((w_out, h_out), Image.LANCZOS)


CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:%(W)spx; height:1080px; overflow:hidden; background:#000; font-family:'Noto Sans SC', sans-serif; }
.bg { position:absolute; inset:0; background:url(%(BG)s) center/cover no-repeat; filter:brightness(.9) saturate(1.05); }
.shade { position:absolute; left:0; right:0; bottom:0; height:%(SH)spx; background:linear-gradient(to top, rgba(0,0,0,.92) 0%%, rgba(0,0,0,.78) 55%%, rgba(0,0,0,0) 100%%); }
.top { position:absolute; left:0; right:0; top:0; height:300px; background:linear-gradient(to bottom, rgba(0,0,0,.62), rgba(0,0,0,0)); }
.abs { position:absolute; }
.plate { background:#FF4F1A; color:#fff; border-radius:22px; font:900 %(PL)spx/1.1 'Noto Sans SC'; padding:.14em .42em; white-space:nowrap; box-shadow:0 14px 34px rgba(0,0,0,.45); letter-spacing:.02em; }
.badge { background:rgba(255,255,255,.94); color:#111; border-radius:999px; font:800 %(BD)spx 'Noto Sans SC'; padding:.16em .7em; white-space:nowrap; }
.l1 { color:#FFD84D; font:900 %(L1)spx/1.15 'Noto Sans SC'; white-space:nowrap; -webkit-text-stroke:8px #000; paint-order:stroke fill; }
.l2 { color:#fff; font:900 %(L2)spx/1.12 'Noto Sans SC'; white-space:nowrap; -webkit-text-stroke:12px #000; paint-order:stroke fill; }
.l2 b { color:#FFD84D; font-weight:900; }
.l3 { display:inline-block; background:#FFD84D; color:#111; border-radius:24px; font:900 %(L3)spx/1.12 'Noto Sans SC'; padding:.08em .36em; white-space:nowrap; box-shadow:0 14px 34px rgba(0,0,0,.5); }
</style>
"""


def page(w, im):
    if w == 1920:
        p = dict(W=1920, SH=470, PL=100, BD=40, L1=60, L2=106, L3=112)
        bg = crop(im, im.width / 2, 860, 1920, 1080)
        body = """
<div class="abs plate" style="left:64px; top:56px;">《超级智能协定》</div>
<div class="abs badge" style="right:64px; top:70px;">白宫 · 2026.9.29</div>
<div class="abs" style="left:70px; top:690px;">
  <div class="l1">一个视频带你看懂：</div>
  <div class="l2">昨天<b>川普</b>和<b>6位CEO</b></div>
  <div style="margin-top:14px;"><span class="l3">到底签署了啥？</span></div>
</div>"""
    else:
        p = dict(W=1440, SH=520, PL=84, BD=34, L1=56, L2=96, L3=100)
        bg = crop(im, im.width / 2, 860, 1440, 1080)
        body = """
<div class="abs plate" style="left:48px; top:48px;">《超级智能协定》</div>
<div class="abs badge" style="left:48px; top:206px;">白宫 · 2026.9.29</div>
<div class="abs" style="left:56px; top:700px;">
  <div class="l1">一个视频带你看懂：</div>
  <div class="l2">昨天<b>川普</b>和<b>6位CEO</b></div>
  <div style="margin-top:14px;"><span class="l3">到底签署了啥？</span></div>
</div>"""
    p["BG"] = data_uri(bg)
    return (CSS % p) + '<div class="bg"></div><div class="top"></div><div class="shade"></div>' + body


def main():
    wide, close = frame(64.0), frame(112.0)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for tag, im in (("C", wide), ("D", close)):
            for w, name in ((1920, "16x9"), (1440, "4x3")):
                pg = b.new_page(viewport={"width": w, "height": 1080})
                pg.set_content("<!doctype html><html><head><meta charset='utf-8'></head><body>" + page(w, im) + "</body></html>")
                pg.evaluate("document.fonts.ready.then(() => true)")
                pg.wait_for_timeout(700)
                out = HERE / f"封面_{tag}_{name}.png"
                pg.screenshot(path=str(out))
                print("->", out.name)
                pg.close()
        b.close()
    for name in ("16x9", "4x3"):
        shutil.copy2(HERE / f"封面_C_{name}.png", HERE / f"封面_选定_{name}.png")
    print("封面_选定_* = C")


if __name__ == "__main__":
    main()
