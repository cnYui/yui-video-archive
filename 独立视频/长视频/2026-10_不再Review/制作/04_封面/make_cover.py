# -*- coding: utf-8 -*-
r"""《不再 Review》封面候选：A / B / C 三个，每个 16:9（1920×1080）和 4:3（1440×1080）。
封面协定（AGENTS.md「封面和标题」）：只放几个简短的大字，不放小字；标题写详细，不和封面同一句。16:9 的字和主体收在 B 站首页的 16:10 安全区里（x 96–1824）。

  A  Lauren 的安静帧（访谈 2962.5 s，Matt 提问时她在听，笑、闭嘴、正对镜头；原画面是左右并排的两个人，取她那一半）+ “不再Review”（主角放大）
  B  她演讲里的三张 GitHub 贡献曲线（“i shipped 5000+ PRs in 6 months”）+ “2000个PR / 谁来审？”（数字钩子）
  C  访谈的并排画面（Matt 左、Lauren 右）+ “AI自己合并”（她原话：agents are merging their own code while I sleep）

  python make_cover.py [A B C]      出 封面_<名>_16x9.png / 封面_<名>_4x3.png；--select <名> 把它复制成 封面_选定_16x9.png / _4x3.png
素材图在 _src/（ffmpeg 从访谈 / 演讲视频抽的；都是第三方画面，不进 git，成品 png 也不进 git）。
"""
import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "_src"
FONTS = "file:///D:/大疆/AI科普/素材/字体/fonts.css"
INK, ORANGE, YEL, PAPER = "#1B1B1F", "#FF4F1A", "#FFD84D", "#FAF9F5"
SIZES = {"16x9": (1920, 1080), "4x3": (1440, 1080), "3x4": (1080, 1440)}      # 3x4 只有 A 有版式（抖音竖封面 / 小红书 / 视频号用，2026-10-05 加）

CSS = f"""
* {{ box-sizing:border-box; margin:0; padding:0; }}
html, body {{ background:{PAPER}; overflow:hidden; font-family:'Noto Sans SC', sans-serif; }}
.abs {{ position:absolute; }}
.frame {{ position:absolute; background:#fff; padding:14px; border:5px solid {INK}; box-shadow:16px 16px 0 {INK}; }}
.frame img {{ display:block; width:100%; height:100%; object-fit:cover; }}
.big {{ position:absolute; font-weight:900; line-height:1; letter-spacing:-0.02em; white-space:nowrap; color:{INK}; }}
.or {{ color:{ORANGE}; }}
.hl {{ background:linear-gradient(transparent 60%, {YEL} 60%, {YEL} 92%, transparent 92%); padding:0 .04em; }}
.wh {{ color:#fff; -webkit-text-stroke:0; text-shadow:0 6px 0 rgba(0,0,0,.55); }}
"""

# 每个候选、每种比例的版式：img = 图片文件；frame = (left, top, width, height)（含内边距之内的图框大小）；texts = [(html, left, top, 字号, 最大宽度, class)]
LAYOUTS = {
    "A": {
        "16x9": dict(img="lauren_calm.png", frame=(933, 41, 853, 960),
                     texts=[("不再", 96, 130, 380, 800, ""), ("Review", 96, 560, 250, 800, "or hl")]),
        "4x3": dict(img="lauren_calm_wide.png", frame=(60, 372, 1320, 640),
                    texts=[("不再Review", 60, 70, 205, 1320, "")], mark_or="Review"),
        "3x4": dict(img="lauren_calm.png", frame=(190, 575, 700, 787),
                    texts=[("不再", 90, 40, 300, 900, ""), ("Review", 90, 345, 190, 900, "or hl")]),
    },
    "B": {
        "16x9": dict(img="chart.png", frame=(1000, 150, 770, 750),
                     texts=[("2000个PR", 96, 150, 215, 850, ""), ("谁来审？", 96, 520, 250, 850, "or hl")]),
        "4x3": dict(img="chart.png", frame=(380, 330, 680, 662),
                    texts=[("2000个PR谁来审？", 60, 80, 150, 1320, "")], mark_or="谁来审？"),
    },
    "C": {
        "16x9": dict(img="twoup.png", full=True,
                     texts=[("AI自己合并", 96, 770, 270, 1560, "wh")]),
        "4x3": dict(img="twoup_43.png", full=True,
                    texts=[("AI自己合并", 60, 800, 210, 1320, "wh")]),
    },
}


def page_html(name, ratio):
    w, h = SIZES[ratio]
    L = LAYOUTS[name][ratio]
    body = []
    if L.get("full"):
        body.append(f'<img class="abs" src="{(SRC / L["img"]).as_uri()}" style="left:0;top:0;width:{w}px;height:{h}px;object-fit:cover">')
        body.append(f'<div class="abs" style="left:0;top:{h - 520}px;width:{w}px;height:520px;background:linear-gradient(transparent, rgba(0,0,0,.78) 55%)"></div>')
    else:
        fl, ft, fw, fh = L["frame"]
        body.append(f'<div class="frame" style="left:{fl}px;top:{ft}px;width:{fw + 38}px;height:{fh + 38}px"><img src="{(SRC / L["img"]).as_uri()}"></div>')
    for i, (txt, x, y, fs, maxw, cls) in enumerate(L["texts"]):
        if "mark_or" in L and L["mark_or"] in txt:
            txt = txt.replace(L["mark_or"], f'<span class="or hl">{L["mark_or"]}</span>')
        if "hl2" in cls:
            txt = f'<span class="hl" style="background:linear-gradient(transparent 60%, {ORANGE} 60%, {ORANGE} 94%, transparent 94%)">{txt}</span>'
        body.append(f'<div class="big {cls}" data-fit="{maxw}" style="left:{x}px;top:{y}px;font-size:{fs}px">{txt}</div>')
    return (f'<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="{FONTS}"><style>{CSS} html,body{{width:{w}px;height:{h}px}}</style>'
            f'<body>{"".join(body)}</body>')


FIT = """
() => { for (const el of document.querySelectorAll('[data-fit]')) { const mx = +el.dataset.fit; let fs = parseFloat(el.style.fontSize);
  while (el.getBoundingClientRect().width > mx && fs > 40) { fs *= 0.97; el.style.fontSize = fs + 'px'; } }
  return [...document.querySelectorAll('[data-fit]')].map(e => [e.textContent, Math.round(parseFloat(e.style.fontSize)), Math.round(e.getBoundingClientRect().left), Math.round(e.getBoundingClientRect().right)]); }
"""


def prep_sources():
    """4:3 要用的图：A 取她这一半的上半身横幅，C 取并排画面中间 1440 宽。"""
    from PIL import Image
    im = Image.open(SRC / "lauren_calm.png")                       # 960×1080
    im.crop((0, 120, 960, 120 + 465)).save(SRC / "lauren_calm_wide.png")      # 960×465（脸和肩膀），框是 1320×640，object-fit: cover 会再裁一点
    tw = Image.open(SRC / "twoup.png")                             # 1920×1080
    tw.crop((240, 0, 1680, 1080)).save(SRC / "twoup_43.png")      # 两个人的脸在 x≈480 和 x≈1440，居中裁 1440 宽都留得下


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--select" in sys.argv:
        k = sys.argv[sys.argv.index("--select") + 1]
        for r in SIZES:
            if (HERE / f"封面_{k}_{r}.png").is_file():
                shutil.copy(HERE / f"封面_{k}_{r}.png", HERE / f"封面_选定_{r}.png")
        print("选定", k)
        return
    names = args or list(LAYOUTS)
    prep_sources()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for n in names:
            for r, (w, h) in SIZES.items():
                if r not in LAYOUTS[n]:
                    continue
                pg = b.new_page(viewport={"width": w, "height": h})
                html = HERE / f"_cover_{n}_{r}.html"
                html.write_text(page_html(n, r), encoding="utf-8")
                pg.goto(html.as_uri())
                pg.evaluate("document.fonts.ready.then(() => true)")
                pg.wait_for_timeout(400)
                fit = pg.evaluate(FIT)
                pg.screenshot(path=str(HERE / f"封面_{n}_{r}.png"))
                pg.close()
                print(n, r, fit)
        b.close()


if __name__ == "__main__":
    main()
