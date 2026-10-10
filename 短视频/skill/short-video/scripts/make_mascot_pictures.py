# -*- coding: utf-8 -*-
r"""封面用的“Claude 八爪鱼”画面（官方课里 Claude Code 的橙色像素吉祥物，见 assets/mascot/README.md）。

  python make_mascot_pictures.py <本条目录> [--prompt "> claude"]

出三张 1150×1000 的画面到 <本条>\制作\04_封面\_src\：
  M_A.png  官方米色底 + 一只大的 + 脚下影子 + 几颗像素小星光
  M_B.png  深色终端底（#141413）：三个窗口点 + 吉祥物 + “> claude”提示符 + 光标块（--prompt 改提示符文字）
  M_C.png  淡黄底（#F5DB9A）：一只大的带三只小的（官方动画里的“一队 agent”）
再在 制作\04_封面\candidates_framed.json 里把 video 指向它们（t 写 0、crop 写 [0,0,1,1]），big 写压缩的钩子（例：["一个视频入门", "Claude Code"]），
sticker 写“官方教程 第N期”，跑 make_cover_framed.py 加大字 + 边框 + 贴纸。形象不重新上色、不改形状。
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SK = Path(__file__).resolve().parents[1]
SP = json.loads((SK / "assets" / "mascot" / "mascot_sprite.json").read_text(encoding="utf-8"))
GRID = SP["grid"]
ORANGE, EYE = (217, 119, 87), (0, 0, 0)               # 品牌橙 #D97757；眼睛官方是纯黑
BEIGE, DARK, IVORY, YELLOW = (226, 216, 203), (20, 20, 19), (250, 249, 245), (245, 219, 154)
DEEP = (191, 104, 76)                                  # 深橙 #BF684C（小星光）
MONO = Path(r"D:\大疆\AI科普\素材\字体\JetBrainsMono.ttf")
W, H = 1150, 1000


def draw_sprite(d, x, y, s):
    for r, row in enumerate(GRID):
        for c, ch in enumerate(row):
            if ch in "OK":
                d.rectangle([x + c * s, y + r * s, x + (c + 1) * s - 1, y + (r + 1) * s - 1], fill=EYE if ch == "K" else ORANGE)


def sparkle(d, cx, cy, u, color):
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        d.rectangle([cx + dx * u, cy + dy * u, cx + dx * u + u - 1, cy + dy * u + u - 1], fill=color)


def pic_a(out):
    im = Image.new("RGB", (W, H), BEIGE)
    d = ImageDraw.Draw(im)
    s = 78
    x, y = (W - 12 * s) // 2, 215
    draw_sprite(d, x, y, s)
    d.rectangle([x + 2 * s, y + 8 * s + 14, x + 10 * s - 1, y + 8 * s + 14 + s // 3], fill=(208, 196, 180))      # 脚下的影子
    for cx, cy, u, col in ((140, 170, 14, ORANGE), (1000, 250, 10, ORANGE), (1040, 700, 14, DEEP), (120, 760, 10, DEEP), (930, 130, 8, DEEP)):
        sparkle(d, cx, cy, u, col)
    im.save(out / "M_A.png")


def pic_b(out, prompt):
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    for i, col in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        d.ellipse([46 + i * 52, 44, 46 + i * 52 + 30, 74], fill=col)
    s = 70
    x, y = (W - 12 * s) // 2, 170
    draw_sprite(d, x, y, s)
    f = ImageFont.truetype(str(MONO), 92)
    tw = d.textlength(prompt, font=f)
    tx, ty = (W - tw) / 2 - 20, y + 8 * s + 90
    d.text((tx, ty), prompt, font=f, fill=IVORY)
    d.rectangle([tx + tw + 14, ty + 8, tx + tw + 14 + 52, ty + 92], fill=ORANGE)                                    # 光标块
    im.save(out / "M_B.png")


def pic_c(out):
    im = Image.new("RGB", (W, H), YELLOW)
    d = ImageDraw.Draw(im)
    s = 66
    draw_sprite(d, (W - 12 * s) // 2, 120, s)
    s2, gap = 24, 52
    x2 = (W - (3 * 12 * s2 + 2 * gap)) // 2
    for i in range(3):
        draw_sprite(d, x2 + i * (12 * s2 + gap), 120 + 8 * s + 90, s2)
    for cx, cy, u in ((150, 160, 12), (1010, 200, 10), (1050, 400, 12)):
        sparkle(d, cx, cy, u, DEEP)
    im.save(out / "M_C.png")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    out = Path(args[0]) / "制作" / "04_封面" / "_src"
    out.mkdir(parents=True, exist_ok=True)
    prompt = args[args.index("--prompt") + 1] if "--prompt" in args else "> claude"
    pic_a(out)
    pic_b(out, prompt)
    pic_c(out)
    print("ok:", ", ".join(sorted(p.name for p in out.glob("M_*.png"))), "→", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
