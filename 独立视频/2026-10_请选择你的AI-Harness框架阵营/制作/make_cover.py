# -*- coding: utf-8 -*-
"""封面：用开头的标题画面（三行标题 + 16 个 logo）重新排成 B 站要的两个比例。
输出 制作/04_封面/封面_16x9_1920x1080.png 和 封面_4x3_1440x1080.png。
（视频真正的第 0 帧是空的——标题要等第一拍才盖章——所以封面取的是“开头那个标题画面”。）
"""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
OUT = HERE / "04_封面"
SCRIPT = HERE.parent / "台本" / "台本.json"
SIZES = {"16x9": (1920, 1080), "4x3": (1440, 1080)}


def main():
    data = json.loads(SCRIPT.read_text(encoding="utf-8"))
    for lid, L in data["logos"].items():
        f = L.get("file")
        if f:
            p = HERE / "assets" / "logos" / f
            L["file"] = p.resolve().as_uri() if p.exists() else None
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=["--force-device-scale-factor=1", "--font-render-hinting=none", "--disable-lcd-text"])
        for ratio, (w, h) in SIZES.items():
            page = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
            page.add_init_script("window.DATA = " + json.dumps(data, ensure_ascii=False) + f"; window.RATIO = '{ratio}';")
            page.goto((OUT / "cover.html").resolve().as_uri())
            page.evaluate("window.__ready")
            out = OUT / f"封面_{ratio}_{w}x{h}.png"
            page.screenshot(path=str(out), type="png")
            print(out.name, out.stat().st_size // 1024, "KB")
        b.close()


if __name__ == "__main__":
    main()
