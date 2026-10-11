# -*- coding: utf-8 -*-
"""封面：取原片里一帧（t = 12.3 s，正对镜头），下三分之一压暗，打上标题。出 16:9（1920×1080）和 4:3（1440×1080）各一张。

  python make_cover.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT = Path(r"D:/大疆/AI科普/素材/字体/NotoSansSC.ttf")
BASE = HERE / "cand" / "f_12.3.png"
LINE1, LINE2 = "演示出岔子了", "OpenAI 重演 dots"
TAG = "DevDay 2026｜AI 助理订机票 · 订酒店 · 理反馈｜中文同传"
YELLOW, WHITE = (255, 216, 74), (255, 255, 255)


def font(size, weight=800):
    f = ImageFont.truetype(str(FONT), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def text_w(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def compose(img, name):
    W, H = img.size
    # 下面 45% 渐变压暗，保证白字和黄字清楚
    g = Image.new("L", (1, H), 0)
    top = int(H * 0.52)
    for y in range(top, H):
        g.putpixel((0, y), int(185 * (y - top) / (H - top)))
    shade = Image.new("RGB", (W, H), (8, 10, 14))
    img = Image.composite(shade, img, g.resize((W, H)))
    d = ImageDraw.Draw(img)
    s = W / 1920
    f1, f2, f3 = font(int(132 * s)), font(int(100 * s)), font(int(40 * s), 600)
    y = int(H * 0.60)
    for txt, f, col, gap in ((LINE1, f1, YELLOW, int(22 * s)), (LINE2, f2, WHITE, int(34 * s))):
        x = (W - text_w(d, txt, f)) // 2
        d.text((x, y), txt, font=f, fill=col, stroke_width=int(9 * s), stroke_fill=(14, 14, 18))
        y += int(f.size * 1.18) + gap
    w3 = text_w(d, TAG, f3)
    pad = int(26 * s)
    x3, y3 = (W - w3) // 2, int(H * 0.915)
    d.rounded_rectangle((x3 - pad, y3 - int(12 * s), x3 + w3 + pad, y3 + int(f3.size * 1.25)), radius=int(22 * s), fill=(0, 0, 0, 160))
    d.text((x3, y3), TAG, font=f3, fill=WHITE)
    img.save(HERE / name)
    print(name, img.size)


def main():
    base = Image.open(BASE).convert("RGB")
    compose(base.copy(), "封面_v1_16x9.png")
    left = (1920 - 1440) // 2 - 60                       # 4:3：取中间偏左一点，让人物居中
    compose(base.crop((left, 0, left + 1440, 1080)), "封面_v1_4x3.png")


if __name__ == "__main__":
    main()
