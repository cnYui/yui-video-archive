# -*- coding: utf-8 -*-
"""封面 E（用户 2026-10-01 晚的要求）：背景用用户给的七张人脸特写拼图，封面上只保留《超级智能协定》这几个字（用户：“封面图只保留 超级智能协定 就可以”），后来要求字大一些、黄色、放在封面正中间。

  python make_cover3.py → 封面_E_16x9.png / 封面_E_4x3.png；封面_选定_* = E（C、D 还在）

背景图：素材/用户提供/封面背景_七张脸.png（1254×1254，内容区 10–1243 × 10–1113，上排 3 张、下排 4 张；用户给的）。
排版：拼图整高居中（两个比例都一样），两边是同一张图放大、模糊、压暗的底；《超级智能协定》黄色大字（黑描边）压在正中间。
先前几版：带“绷不住了！”等标题字的一版、橙色小标贴左上角的一版，都留在 _bg/。
"""
import base64
import io
import shutil
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "素材" / "用户提供" / "封面背景_七张脸.png"


def data_uri(im, q=95):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:__W__px; height:1080px; overflow:hidden; background:#000; font-family:'Noto Sans SC', sans-serif; }
.bgblur { position:absolute; inset:-60px; background:url(__BG__) center/cover no-repeat; filter:blur(30px) brightness(.5) saturate(1.1); }
.abs { position:absolute; }
.big { position:absolute; left:0; right:0; top:0; height:1080px; display:flex; align-items:center; justify-content:center; color:#FFD84D; font:900 __PL__px/1.1 'Noto Sans SC'; white-space:nowrap; letter-spacing:.02em; -webkit-text-stroke:__ST__px #000; paint-order:stroke fill; text-shadow:0 10px 36px rgba(0,0,0,.65); }
</style>
"""


def page(w, content):
    ch = 1080
    cw = round(content.width * ch / content.height)                  # 1207
    left = (w - cw) // 2
    col = content.resize((cw, ch), Image.LANCZOS)
    pl, st = (176, 16) if w == 1920 else (134, 13)               # 16:9 一行 8 个字约 1410 px；4:3 约 1070 px（拼图宽 1207）
    s = CSS.replace("__W__", str(w)).replace("__PL__", str(pl)).replace("__ST__", str(st)).replace("__BG__", data_uri(content, 88))
    body = f"""
<div class="bgblur"></div>
<div class="abs" style="left:{left}px; top:0; width:{cw}px; height:{ch}px; background:url({data_uri(col)}) center/100% 100%; box-shadow:0 0 70px rgba(0,0,0,.6);"></div>
<div class="big">《超级智能协定》</div>"""
    return s + body


def main():
    im = Image.open(SRC).convert("RGB")
    content = im.crop((10, 10, 1244, 1114))                          # 去掉外圈和下面的白边：1234×1104
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for w, name in ((1920, "16x9"), (1440, "4x3")):
            pg = b.new_page(viewport={"width": w, "height": 1080})
            pg.set_content("<!doctype html><html><head><meta charset='utf-8'></head><body>" + page(w, content) + "</body></html>")
            pg.evaluate("document.fonts.ready.then(() => true)")
            pg.wait_for_timeout(900)
            out = HERE / f"封面_E_{name}.png"
            pg.screenshot(path=str(out))
            print("->", out.name)
            pg.close()
        b.close()
    for name in ("16x9", "4x3"):
        shutil.copy2(HERE / f"封面_E_{name}.png", HERE / f"封面_选定_{name}.png")
    print("封面_选定_* = E（C、D 还在）")


if __name__ == "__main__":
    main()
