# -*- coding: utf-8 -*-
"""背景印花：用各家 AI 编程工具的图标（Claude Code / Codex / Trae / WorkBuddy / Cursor / Windsurf …）铺成低透明度的重复图案，贴在米白底上。
图标来自 独立视频\\2026-10_请选择你的AI-Harness框架阵营\\制作\\assets\\logos（LobeHub 图标 + 各家官方 favicon / 应用图标）。

  python make_pattern.py   →  pattern_color.png（原色，淡）/ pattern_ink.png（墨色单色）/ pattern_orange.png（橙色单色）/ pattern_none.png（只有原来的点阵）
每张都是 1080×2340、透明底（透明度已经烤进去），用法：背景 div 的 background-image，底色仍是 #FAF9F5。
"""
import random
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

LOGOS = Path(r"D:\大疆\独立视频\2026-10_请选择你的AI-Harness框架阵营\制作\assets\logos")
OUT = Path(__file__).resolve().parent
ICON_DIR = OUT / "_icons"
W, H = 1080, 2340

# (名字, 文件)：能带颜色的用 -color 版，没有的用单色版；workbuddy 是 png
ICONS = [
    ("claudecode", "lobe_claudecode-color.svg"), ("codex", "lobe_codex-color.svg"), ("trae", "lobe_trae-color.svg"), ("workbuddy", "workbuddy.png"),
    ("cursor", "lobe_cursor.svg"), ("windsurf", "windsurf_windsurf-black-symbol.svg"), ("copilot", "lobe_copilot-color.svg"), ("geminicli", "lobe_geminicli-color.svg"),
    ("kiro", "lobe_kiro-color.svg"), ("antigravity", "lobe_antigravity-color.svg"), ("cline", "lobe_cline.svg"), ("opencode", "lobe_opencode.svg"),
    ("qoder", "lobe_qoder-color.svg"), ("codebuddy", "lobe_codebuddy-color.svg"), ("openhands", "lobe_openhands-color.svg"), ("devin", "lobe_devin-color.svg"),
]


MONO = {"claudecode": "lobe_claudecode.svg", "codex": "lobe_codex.svg", "trae": "lobe_trae.svg", "workbuddy": "workbuddy.png", "cursor": "lobe_cursor.svg",
        "windsurf": "windsurf_windsurf-black-symbol.svg", "copilot": "lobe_githubcopilot.svg", "geminicli": "lobe_geminicli.svg", "kiro": "lobe_kiro.svg",
        "antigravity": "lobe_antigravity.svg", "cline": "lobe_cline.svg", "opencode": "lobe_opencode.svg", "qoder": "lobe_qoder.svg", "codebuddy": "lobe_codebuddy.svg",
        "openhands": "lobe_openhands.svg", "devin": "lobe_devin.svg"}


def rasterize():
    """每个图标渲成 256×256 透明底 PNG（SVG 交给 Chromium 画）。"""
    ICON_DIR.mkdir(exist_ok=True)
    html = ICON_DIR / "_r.html"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 256, "height": 256})
        for name, f in ICONS + [(n + "_mono", f) for n, f in MONO.items()]:
            src = (LOGOS / f).as_uri()
            html.write_text(f'<!doctype html><body style="margin:0;background:transparent"><img id="i" src="{src}" style="width:256px;height:256px;object-fit:contain;display:block"></body>', encoding="utf-8")
            pg.goto(html.as_uri())
            pg.wait_for_function("document.getElementById('i').complete")
            pg.screenshot(path=str(ICON_DIR / f"{name}.png"), omit_background=True, clip={"x": 0, "y": 0, "width": 256, "height": 256})
        b.close()


def tint(im, rgb):
    """把图标整个染成一种颜色（保留透明度）。"""
    a = im.getchannel("A")
    out = Image.new("RGBA", im.size, rgb + (0,))
    out.putalpha(a)
    return out


def make(variant, opacity, step_x, step_y, size, seed):
    rnd = random.Random(seed)
    icons = []
    for name, _ in ICONS:
        im = Image.open(ICON_DIR / (f"{name}_mono.png" if variant != "color" else f"{name}.png")).convert("RGBA")
        if variant != "color" and name == "workbuddy":          # 应用图标是满版方块：用亮度当透明度，剩下图形
            g = im.convert("L")
            im.putalpha(g.point(lambda v: 255 - v) if sum(g.getdata()) / (256 * 256) > 128 else g)
        if variant == "ink":
            im = tint(im, (20, 20, 19))
        elif variant == "orange":
            im = tint(im, (255, 79, 26))
        icons.append(im)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    order = list(range(len(icons)))
    k, row = 0, 0
    y = -step_y // 2
    while y < H + step_y:
        x = -step_x // 2 + (step_x // 2 if row % 2 else 0)
        while x < W + step_x:
            if k % len(order) == 0:
                rnd.shuffle(order)
            im = icons[order[k % len(order)]]
            s = int(size * rnd.uniform(0.86, 1.12))
            t = im.resize((s, s), Image.LANCZOS).rotate(rnd.uniform(-14, 14), resample=Image.BICUBIC, expand=True)
            a = t.getchannel("A").point(lambda v: int(v * opacity))
            t.putalpha(a)
            canvas.alpha_composite(t, (int(x - t.width / 2 + rnd.uniform(-8, 8)), int(y - t.height / 2 + rnd.uniform(-8, 8))))
            x += step_x
            k += 1
        y += step_y
        row += 1
    return canvas


def main():
    rasterize()
    make("color", 0.11, 176, 168, 76, 7).save(OUT / "pattern_color.png")
    make("ink", 0.075, 176, 168, 76, 11).save(OUT / "pattern_ink.png")
    make("orange", 0.12, 176, 168, 76, 13).save(OUT / "pattern_orange.png")
    Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(OUT / "pattern_none.png")
    print("ok", [p.name for p in OUT.glob("pattern_*.png")])


if __name__ == "__main__":
    main()
