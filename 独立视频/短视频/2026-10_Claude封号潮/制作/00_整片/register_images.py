# -*- coding: utf-8 -*-
"""把文章里的原图（官方页面截图、作者的信息图）裁一块、登记成 pageShot 能用的“页面图”，不用重新上网截。
输出 media/pages/<名字>.png，并把 {src, w, h, url, bg, marks} 写进 pages.json / pages.js（和 capture_pages.py 共用同一个文件，互不覆盖）。

  python register_images.py            全部重登记
  python register_images.py A_trust …  只登记指定的几张

marks 的坐标写**原图像素**（x, y, w, h），脚本按裁切框换算；键以 "#sel:" 开头 = 画橙色边框（整块），否则 = 荧光笔。
scenes.js 里 pageShot(…, [[标记名, 时刻, 中文译文], …]) 用的就是这里的标记名。
"""
import json
import sys
from pathlib import Path

from PIL import Image

from common import MAT

HERE = Path(__file__).resolve().parent
OUT = HERE / "media" / "pages"
IMG = MAT / "2026-10_Claude封号潮" / "文章配图"

# 名字: dict(src=原图文件名, crop=(x0, y0, x1, y1) 原图像素, url=浏览器顶栏里显示的网址, marks={标记名: (x, y, w, h)})
SPECS = {
    # 官方「System Trust and Reporting」页（作者的截图，页面标注 Last updated July 23, 2026）：封号数 / 申诉数 / 推翻数
    "A_trust": dict(src="03_块020_2106432943119867904.jpg", crop=(1240, 250, 2640, 2160), url="https://www.anthropic.com/transparency/system-trust-reporting",
                    marks={"updated": (1270, 386, 400, 52),
                           "num114": (1560, 820, 720, 118),
                           "#sel:big114": (1540, 815, 760, 280),
                           "#sel:appeals": (1420, 1525, 1000, 275),
                           "enforce": (1270, 1150, 1290, 312),
                           "enforce_end": (1270, 1305, 1290, 155),
                           "prev": (1270, 1996, 530, 46),
                           "period114": (1770, 1040, 300, 40)}),
    # 官方帮助中心「Safeguards warnings and appeals」（作者的截图，页面标注 July 9, 2026）。字太小，拆成两张：A_help 只裁“理由”那一块（字放大），A_help2 是申诉 / 导出数据两段（整段宽）
    "A_help": dict(src="02_块014_2106432926673932290.jpg", crop=(1090, 745, 2205, 1100), url="https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals",
                   marks={"intro": (1100, 840, 1100, 42),
                          "b1": (1120, 917, 610, 44),
                          "b2": (1120, 980, 730, 44),
                          "b3": (1120, 1042, 440, 44),
                          "#sel:list": (1100, 905, 770, 186)}),
    "A_help2": dict(src="02_块014_2106432926673932290.jpg", crop=(1090, 1100, 2790, 1900), url="https://support.claude.com/en/articles/8241253-safeguards-warnings-and-appeals",
                    marks={"appeal_p": (1100, 1120, 1660, 130),
                           "important": (1100, 1455, 1660, 125),
                           "export_h": (1100, 1660, 950, 56),
                           "export_p": (1100, 1738, 1660, 138)}),
    # 作者的信息图（2560×1440）：被封了先分清是哪一种
    "A_flow": dict(src="16_块199_2106433367990247424.jpg", crop=None, url="https://x.com/i/article/2106425943061413888（AYi 的文章配图）",
                   marks={"#sel:banned": (1260, 880, 1330, 120), "#sel:steps": (1294, 1117, 1072, 109)}),
    # 文章封面
    "A_cover": dict(src="00_封面_HTxECanXIAA7Dlw.jpg", crop=None, url="https://x.com/i/article/2106425943061413888", marks={"#sel:cover": (40, 40, 3280, 1264)}),
}


def main():
    only = sys.argv[1:] or list(SPECS)
    OUT.mkdir(parents=True, exist_ok=True)
    mf = HERE / "pages.json"
    meta = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    for k in only:
        s = SPECS[k]
        im = Image.open(IMG / s["src"]).convert("RGB")
        x0, y0, x1, y1 = s.get("crop") or (0, 0, im.width, im.height)
        cr = im.crop((x0, y0, x1, y1))
        f = OUT / f"{k}.png"
        cr.save(f)
        ms = {}
        for name, r in s.get("marks", {}).items():
            rects = r if isinstance(r[0], (list, tuple)) else [r]
            ms[name] = [[int(round(x - x0)), int(round(y - y0)), int(round(w)), int(round(h))] for x, y, w, h in rects]
        bg = "#%02X%02X%02X" % cr.getpixel((6, cr.height - 6))
        meta[k] = {"src": f"pages/{k}.png", "w": cr.width, "h": cr.height, "url": s["url"], "bg": bg, "marks": ms}
        print(f"{k}: {cr.width}×{cr.height}，标记 {len(ms)} 个，底色 {bg}")
    mf.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "pages.js").write_text("window.PG = " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
