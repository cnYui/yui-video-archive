# -*- coding: utf-8 -*-
r"""封面“Claude 八爪鱼形象”版（用户 2026-10-06：“封面做成带有 claude 八爪鱼形象的一个封面，上面你给的三个封面都不太行”，字用“一个视频入门 Claude Code”）。

形象 = 官方课（Claude Academy · CC101-06 上下文管理 30.4 s）里 Claude Code 的橙色像素吉祥物，12×8 方块（mascot_sprite.json，从官方帧原样还原，不重新上色、不自己改形状）。
这里只出“画面”（边框里的图）：_src/M_A.png / M_B.png / M_C.png；大字 + 边框 + 贴纸由技能的 make_cover_framed.py 加（candidates_framed.json 里 video 指向这三张图）。
  A 官方米色底，一只大吉祥物 + 脚下一条影子 + 几颗像素小星光
  B 深色终端底（#141413）：吉祥物 + “> claude”提示符
  C 淡黄底（#F5DB9A）：一只大的带三只小的（官方动画里的“一队 agent”）
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = HERE / "_src"
SRC.mkdir(exist_ok=True)
SP = json.loads((HERE / "mascot_sprite.json").read_text(encoding="utf-8"))
GRID = SP["grid"]
ORANGE, EYE = (217, 119, 87), (20, 20, 19)          # 品牌橙 #D97757、眼睛（官方是纯黑，这里用品牌深色 #141413 之外的纯黑也行；保持官方的黑）
EYE = (0, 0, 0)
BEIGE, DARK, IVORY, YELLOW = (226, 216, 203), (20, 20, 19), (250, 249, 245), (245, 219, 154)
MONO = r"D:\大疆\AI科普\素材\字体\JetBrainsMono.ttf"
W, H = 1150, 1000


def draw_sprite(d, x, y, s, orange=ORANGE, eye=EYE):
    """左上角 (x, y)，每格 s px；返回外框 (x0, y0, x1, y1)。"""
    for r, row in enumerate(GRID):
        for c, ch in enumerate(row):
            if ch in "OK":
                d.rectangle([x + c * s, y + r * s, x + (c + 1) * s - 1, y + (r + 1) * s - 1], fill=eye if ch == "K" else orange)
    return x, y, x + len(GRID[0]) * s, y + len(GRID) * s


def sparkle(d, cx, cy, u, color):
    """像素小星光：十字 + 中心"""
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        d.rectangle([cx + dx * u, cy + dy * u, cx + dx * u + u - 1, cy + dy * u + u - 1], fill=color)


def pic_a():
    im = Image.new("RGB", (W, H), BEIGE)
    d = ImageDraw.Draw(im)
    s = 78
    x = (W - 12 * s) // 2
    y = 215
    draw_sprite(d, x, y, s)
    # 脚下的影子（方块风格的一条扁长方形，比米色深一档）
    shadow = (208, 196, 180)
    d.rectangle([x + 2 * s, y + 8 * s + 14, x + 10 * s - 1, y + 8 * s + 14 + s // 3], fill=shadow)
    for (cx, cy, u, col) in ((140, 170, 14, ORANGE), (1000, 250, 10, (217, 119, 87)), (1040, 700, 14, (191, 104, 76)), (120, 760, 10, (191, 104, 76)), (930, 130, 8, (191, 104, 76))):
        sparkle(d, cx, cy, u, col)
    im.save(SRC / "M_A.png")


def pic_b():
    im = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(im)
    # 终端窗口的三个点
    for i, col in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        d.ellipse([46 + i * 52, 44, 46 + i * 52 + 30, 74], fill=col)
    s = 70
    x = (W - 12 * s) // 2
    y = 170
    draw_sprite(d, x, y, s)
    f = ImageFont.truetype(MONO, 92)
    txt = "> claude"
    tw = d.textlength(txt, font=f)
    tx = (W - tw) / 2 - 20
    ty = y + 8 * s + 90
    d.text((tx, ty), txt, font=f, fill=IVORY)
    d.rectangle([tx + tw + 14, ty + 8, tx + tw + 14 + 52, ty + 92], fill=ORANGE)          # 光标块
    im.save(SRC / "M_B.png")


def pic_c():
    im = Image.new("RGB", (W, H), YELLOW)
    d = ImageDraw.Draw(im)
    s = 66
    x = (W - 12 * s) // 2
    draw_sprite(d, x, 120, s)
    s2 = 24
    gap = 52
    total = 3 * 12 * s2 + 2 * gap
    x2 = (W - total) // 2
    for i in range(3):
        draw_sprite(d, x2 + i * (12 * s2 + gap), 120 + 8 * s + 90, s2)
    for (cx, cy, u, col) in ((150, 160, 12, (191, 104, 76)), (1010, 200, 10, (191, 104, 76)), (1050, 400, 12, (191, 104, 76))):
        sparkle(d, cx, cy, u, col)
    im.save(SRC / "M_C.png")


if __name__ == "__main__":
    pic_a(); pic_b(); pic_c()
    print("ok:", [p.name for p in sorted(SRC.glob("M_*.png"))])
