# -*- coding: utf-8 -*-
r"""官网页面录屏用的图：把长视频那期截好的官网高清图（素材\官网截图\*.png）按小节裁一裁，算出要高亮的位置，写成 pages.js（window.PG，pageShot 用）。
和 capture_pages.py 的输出格式一样（media/pages/<名字>.png + pages.js），区别是这里不重新上网截图，直接用已有的图（官网页面 10-03 截的，10-04 抽查数字和原文没变）。

  python make_pages.py            出图 + pages.js
  python make_pages.py --check    另出 media/pages/_check_<名字>.png（把高亮位置画在图上，用来核对坐标）

坐标都写“占原图的比例”（x0, y0, x1, y1）；名字以 #sel: 开头 = 整块画橙色边框（图表、卡片），否则 = 荧光笔涂一块（文字）。
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from common import HERE, PAGES_SRC

OUT = HERE / "media" / "pages"
URL = "https://www.tavus.io/griffin"

# 名字: 原图 / 裁剪（占原图比例）/ 高亮
SPECS = {
    # 官网 05.3 面对面实验：两张卡片（Griffin-Lite 26/54 = 48%，上一代 1/41 = 2.4%）
    "P_study": dict(img="g_study", crop=(0, 0, 1, 1182 / 1730), marks={
        "#sel:card_g": (58 / 1424, 324 / 1730, 1366 / 1424, 736 / 1730),
        "#sel:card_p": (58 / 1424, 752 / 1730, 1366 / 1424, 1162 / 1730),
    }),
    # 官网开头：日期、署名、“第一个通过实时视频图灵测试”那句
    "P_intro": dict(img="g_intro", crop=(0, 0, 1, 1), marks={
        "October 1st, 2026": (0 / 1520, 4 / 1438, 246 / 1520, 42 / 1438),
        "first to pass": (0 / 1520, 795 / 1438, 1072 / 1520, 842 / 1438),
    }),
    # 官网 04.2 turn-based vs full-duplex 示意图
    "P_duplex": dict(img="g_duplex", crop=(0, 0, 1, 1), marks={
        "#sel:cascade": (90 / 1552, 452 / 1224, 1462 / 1552, 698 / 1224),
        "#sel:griffin": (90 / 1552, 724 / 1224, 1462 / 1552, 946 / 1224),
    }),
    # 官网 05.3 的下半：54 人、实验设计段落（从 “54 participants” 往下）
    "P_study2": dict(img="g_study", crop=(0, 300 / 1730, 1, 1), marks={
        "54 participants": (92 / 1424, 388 / 1730, 288 / 1424, 424 / 1730),
        "told matched": (58 / 1424, 1442 / 1730, 1366 / 1424, 1565 / 1730),
    }),
    # 官网 05.2 VideoFDB 生成赛道（NVIDIA 打分）
    "P_fdb": dict(img="g_fdb_gen", crop=(0, 0, 1, 1), marks={
        "#sel:human": (56 / 1552, 362 / 1130, 1496 / 1552, 436 / 1130),
        "#sel:griffin": (56 / 1552, 446 / 1130, 1496 / 1552, 506 / 1130),
        "judge": (646 / 1552, 964 / 1130, 1350 / 1552, 998 / 1130),
    }),
    # 官网 06 安全、限制和责任（只取中间那一栏）
    "P_safety": dict(img="g_safety", crop=(0.20, 0.05, 0.80, 0.93), marks={
        "deceive": (0.2316, 0.4009, 0.7684, 0.5293),
        "not available": (0.2316, 0.7262, 0.7684, 0.8973),
    }),
}


def main():
    check = "--check" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {}
    for name, sp in SPECS.items():
        im = Image.open(PAGES_SRC / f"{sp['img']}.png").convert("RGB")
        W, H = im.size
        cx0, cy0, cx1, cy1 = sp["crop"]
        box = (round(cx0 * W), round(cy0 * H), round(cx1 * W), round(cy1 * H))
        cr = im.crop(box)
        cw, ch = cr.size
        marks = {}
        for key, (x0, y0, x1, y1) in sp["marks"].items():
            rx0, ry0 = x0 * W - box[0], y0 * H - box[1]
            rx1, ry1 = x1 * W - box[0], y1 * H - box[1]
            assert -4 <= rx0 and rx1 <= cw + 4 and -4 <= ry0 and ry1 <= ch + 4, f"{name}:{key} 超出裁剪范围 {rx0:.0f},{ry0:.0f},{rx1:.0f},{ry1:.0f} / {cw}×{ch}"
            marks[key] = [[round(rx0), round(ry0), round(rx1 - rx0), round(ry1 - ry0)]]
        f = OUT / f"{name}.png"
        cr.save(f)
        bg = "#%02X%02X%02X" % cr.getpixel((6, ch - 6))
        meta[name] = {"src": f"pages/{name}.png", "w": cw, "h": ch, "url": URL, "bg": bg, "marks": marks}
        print(f"{name}: {cw}×{ch}（原图 {sp['img']}），高亮 {len(marks)} 处，底色 {bg}")
        if check:
            d = cr.copy()
            dr = ImageDraw.Draw(d, "RGBA")
            for key, rs in marks.items():
                for x, y, w, h in rs:
                    if key.startswith("#sel:"):
                        dr.rectangle([x, y, x + w, y + h], outline=(255, 79, 26, 255), width=6)
                    else:
                        dr.rectangle([x, y, x + w, y + h], fill=(255, 205, 40, 110))
            d.save(OUT / f"_check_{name}.png")
    (HERE / "pages.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "pages.js").write_text("window.PG = " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
