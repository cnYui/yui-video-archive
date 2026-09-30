# -*- coding: utf-8 -*-
"""渲染封面：每个方案 16:9（1920×1080）和 4:3（1440×1080）各一张，外加预览（含信息流缩略图大小）。

  python render_covers.py          三个方案 + 封面_三选一_预览.png
  python render_covers.py 4        选定版（cover.html 里的 PICKED）+ 封面_选定_预览.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
NAMES = {1: "方案1_闭眼合十", 2: "方案2_睁眼合十", 3: "方案3_露脸合十", 4: "选定"}


def render(vs):
    outs = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        for v in vs:
            for w, tag in ((1920, "16x9"), (1440, "4x3")):
                page = browser.new_page(viewport={"width": w, "height": 1080})
                errs = []
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.add_init_script(f"window.__COVER__ = {{ v: {v}, w: {w} }};")
                page.goto((HERE / "cover.html").as_uri())
                page.wait_for_function("window.__READY__ === true", timeout=20000)
                out = HERE / f"封面_{NAMES[v]}_{tag}.png"
                page.screenshot(path=str(out))
                page.close()
                if errs:
                    print("ERR", v, tag, errs)
                outs[(v, tag)] = out
                print(out.name)
        browser.close()
    return outs


def sheet(vs, outs, path):
    """每个方案一行：16:9、4:3、信息流大小（约 360×203）。"""
    font = ImageFont.truetype(r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf", 30)
    rowh = 560
    img = Image.new("RGB", (880 + 20 + 660 + 20 + 360 + 60, rowh * len(vs) + 20), "#C9CDD3")
    d = ImageDraw.Draw(img)
    for i, v in enumerate(vs):
        y = 10 + i * rowh
        d.text((20, y), NAMES[v].replace("_", "  "), fill="#111", font=font)
        a = Image.open(outs[(v, "16x9")]).convert("RGB")
        b = Image.open(outs[(v, "4x3")]).convert("RGB")
        img.paste(a.resize((880, 495), Image.LANCZOS), (20, y + 50))
        img.paste(b.resize((660, 495), Image.LANCZOS), (920, y + 50))
        img.paste(a.resize((360, 203), Image.LANCZOS), (1600, y + 50))
        d.text((1600, y + 260), "信息流大小", fill="#333", font=font)
    img.save(path)
    print(path.name)


def main():
    vs = [int(a) for a in sys.argv[1:]] or [1, 2, 3]
    outs = render(vs)
    name = "封面_三选一_预览.png" if vs == [1, 2, 3] else f"封面_{NAMES[vs[0]]}_预览.png"
    sheet(vs, outs, HERE / name)


if __name__ == "__main__":
    main()
