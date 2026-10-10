# -*- coding: utf-8 -*-
"""把原片封面（1280×720，英文标题“How an Anthropic designer uses Claude Slides”）改成中文标题，其他像素一个不动。

  python make_cover_zh.py [--weight 500] [--size 80] [--name 封面]

做法（用户 2026-10-02：“把封面修改为中文，其他不变”）：
  1. 在原图上把文字框里面（框线和四个角点不碰）涂成卡片的米色；
  2. 标题改成两行：“Anthropic 设计师” / “如何使用 **Claude Slides**”。其中 Anthropic 和 Claude Slides（粗体）两个英文词直接从原图里裁下来、贴回去——
     字体和原来一模一样，只有中文字用 Noto Serif SC（思源宋体，Google Fonts）排；基线和原来两行的基线（y=523、y=613）对齐；
  3. 在“Slides”后面补上原来的那根光标。
输出：封面_16x9.png（1280×720，和原图同尺寸）、封面_4x3.png（1280×960：卡片向下接长 240 px，其余不变，给 B 站 4:3 位用）。
"""
import argparse
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
SRC = EP / "素材" / "封面原图_英文.png"
INK = (20, 20, 19)
# 原图量出来的位置（1280×720）
ERASE = (156, 450, 1176, 631)               # 文字框里面要涂掉的矩形（x0, y0, x1, y1），不碰框线（x=142–145 / 1185–1187，y=436–438 / 641–643）和四个角点
L1_BASE, L2_BASE, X0 = 523, 613, 161        # 两行的基线、左边
ANTHROPIC = (454, 460, 832, 545)            # 第一行里 “Anthropic” 的裁剪框（含上下留白）；字形 x=456–830（前面的 “an” 在 351–441，不要），基线 523
CLAUDE_SLIDES = (335, 546, 847, 631)        # 第二行里粗体 “Claude Slides” 的裁剪框（不含光标）；字形左边在 x=337、基线 613
CARET = (851, 545, 855, 629)                # 原来光标的位置（x0, y0, x1, y1：宽 4、高 84，在最后一个 s 右边 5 px），重新画在新的行尾


def pyfont_css(weight):
    return f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@{weight}&display=swap">'


def render_cjk(pw, runs, weight, size):
    """runs = [(文字, 左边 x, 基线 y)]；返回 (透明底的 RGBA 图 1280×720, 每段的宽度)。基线用零宽的 inline-block 量出来对齐。"""
    pg = pw.new_page(viewport={"width": 1280, "height": 720})
    spans = "".join(f'<div class="r" id="r{i}" style="left:{x}px">{t}<i></i></div>' for i, (t, x, _) in enumerate(runs))
    pg.set_content(f"""<!doctype html><html><head><meta charset='utf-8'>{pyfont_css(weight)}<style>
      html,body{{margin:0;background:transparent;width:1280px;height:720px;overflow:hidden}}
      .r{{position:absolute;white-space:nowrap;font:{weight} {size}px/1 'Noto Serif SC',serif;color:rgb({INK[0]},{INK[1]},{INK[2]});top:0}}
      .r i{{display:inline-block;width:0;height:0}}
    </style></head><body>{spans}</body></html>""")
    pg.evaluate("document.fonts.ready.then(() => true)")
    pg.wait_for_timeout(1500)
    info = pg.evaluate("""(runs) => runs.map((r, i) => { const e = document.getElementById('r' + i); const base = e.querySelector('i').getBoundingClientRect().bottom - e.getBoundingClientRect().top;
        return {w: e.getBoundingClientRect().width, base: base}; })""", [list(r) for r in runs])
    for i, (t, x, by) in enumerate(runs):
        pg.evaluate("([i, top]) => { document.getElementById('r' + i).style.top = top + 'px'; }", [i, by - info[i]["base"]])
    pg.wait_for_timeout(300)
    png = pg.screenshot(omit_background=True)
    pg.close()
    return Image.open(io.BytesIO(png)).convert("RGBA"), [i["w"] for i in info]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--weight", type=int, default=500)
    ap.add_argument("--size", type=int, default=80)
    ap.add_argument("--name", default="封面")
    a = ap.parse_args()
    base = Image.open(SRC).convert("RGB")
    arr = np.asarray(base)
    peach = tuple(int(v) for v in np.median(arr[120:140, 300:900].reshape(-1, 3), axis=0))          # 卡片上方空白处的米色
    anth = base.crop(ANTHROPIC)
    cs = base.crop(CLAUDE_SLIDES)
    img = base.copy()
    ImageDraw.Draw(img).rectangle(ERASE, fill=peach)
    gap = round(a.size * 0.26)
    # 第一行：Anthropic（原图裁剪）+ 设计师；第二行：如何使用 + Claude Slides（粗体，原图裁剪）+ 光标
    anth_left = 456 - ANTHROPIC[0]                       # 裁剪图里字形左边的偏移
    cs_left = 337 - CLAUDE_SLIDES[0]
    x_cjk1 = X0 + (831 - 456) + gap                      # Anthropic 字形宽 375（456–830）
    with sync_playwright() as p:
        b = p.chromium.launch()
        layer, widths = render_cjk(b, [("设计师", x_cjk1, L1_BASE), ("如何使用", X0, L2_BASE)], a.weight, a.size)
        b.close()
    img.paste(anth, (X0 - anth_left, ANTHROPIC[1] + 0))                      # y 不变（基线仍是 523）
    x_cs = round(X0 + widths[1] + gap)
    img.paste(cs, (x_cs - cs_left, CLAUDE_SLIDES[1]))
    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    x_end = x_cs + (846 - 337)                           # 粗体 Claude Slides 字形右边
    ImageDraw.Draw(img).rectangle((x_end + 5, CARET[1], x_end + 5 + (CARET[2] - CARET[0]) - 1, CARET[3] - 1), fill=INK)
    out = HERE
    img.save(out / f"{a.name}_16x9.png")
    # 4:3：卡片向下接长 240 px（把最后一行往下重复），其余不变
    last = np.asarray(img)[-1:, :, :]
    ext = np.repeat(last, 240, axis=0)
    Image.fromarray(np.vstack([np.asarray(img), ext])).save(out / f"{a.name}_4x3.png")
    print(json.dumps({"peach": peach, "run_widths": widths, "caption_end_x": x_end, "weight": a.weight, "size": a.size}, ensure_ascii=False))


if __name__ == "__main__":
    main()
