# -*- coding: utf-8 -*-
"""抖音合集封面（1080×1080，≤ 5 MB）：把 B 站有、抖音还没有的四个系列合集补上（用户 2026-10-05：“你把 b 站那边的合集在抖音那边创建一下”）。
按各系列自己的封面风格做：OpenAI相关（黑底白字 + OpenAI 蓝）、原LAI如此（黑板粉笔 + 鲸鱼娘）、AI时代计算机专业研究生如何用AI（白底点阵、浅蓝圆、黑字 + 橙字黄荧光）、Way to AGI（奶油底 + 橙色 AGI）。
"""
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\大疆\AI日报\skill\ai-daily-news\scripts")
import make_cover_white as M  # noqa: E402  (compose_sprite：鲸鱼娘 64×64 像素图)

FONT = r"D:\大疆\AI日报\素材\字体\NotoSansSC.ttf"
CHALK = r"D:\大疆\AI日报\素材\字体\ZCOOLKuaiLe.ttf"
W = 1080
OUT = {
    "openai": Path(r"D:\大疆\OpenAI相关\素材\合集封面"),
    "yuanlai": Path(r"D:\大疆\AI科普\素材\合集封面"),
    "cs": Path(r"D:\大疆\AI震惊瘫坐时代计算机研究生必须掌握的技能\素材\合集封面"),
    "way": Path(r"D:\大疆\Way to AGI\素材\合集封面"),
}


def noto(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([weight])
    return f


def fit(text, weight, max_w, start):
    size = start
    while size > 40:
        f = noto(size, weight)
        if ImageDraw.Draw(Image.new("RGB", (10, 10))).textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return noto(40, weight)


def save(im, key):
    OUT[key].mkdir(parents=True, exist_ok=True)
    p = OUT[key] / "封面_合集_1x1.png"
    im.save(p, optimize=True)
    print(key, p, p.stat().st_size)
    return p


# ---------------------------------------------------------------- OpenAI相关
def openai():
    im = Image.new("RGB", (W, W), "#000000")
    d = ImageDraw.Draw(im)
    blue = "#0285FF"
    f1 = fit("OpenAI", 900, 800, 260)
    f2 = noto(f1.size, 900)
    d.rectangle((92, 250, 106, 790), fill=blue)
    d.text((150, 230), "OpenAI", font=f1, fill="#FFFFFF")
    d.text((150, 230 + int(f1.size * 1.12)), "相关", font=f2, fill=blue)
    d.text((154, 880), "模型实测 · 发布会解读", font=noto(46, 600), fill="#8A8F98")
    return save(im, "openai")


# ---------------------------------------------------------------- 原LAI如此（黑板粉笔）
def yuanlai():
    rnd = np.random.default_rng(7)
    base = np.zeros((W, W, 3), np.float32)
    base[:] = (0x2E, 0x4D, 0x3B)
    base += rnd.normal(0, 3.5, (W, W, 1))                       # 黑板的细噪点
    yy, xx = np.mgrid[0:W, 0:W]
    vig = 1 - 0.18 * (((xx - W / 2) ** 2 + (yy - W / 2) ** 2) ** 0.5 / (W * 0.72)) ** 2
    base *= vig[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W - 1, W - 1), outline="#9C6B3C", width=26)         # 木框
    d.rectangle((26, 960, W - 27, W - 27), fill="#8A5A2B")                # 粉笔槽
    d.rectangle((26, 954, W - 27, 962), fill="#6F4521")
    for x, c, w in ((700, "#F4F1E4", 70), (800, "#F2C94C", 56), (880, "#F4F1E4", 40)):  # 槽里的粉笔头
        d.rounded_rectangle((x, 972, x + w, 990), radius=6, fill=c)

    def chalk(text, size, xy, color, spread=None):
        layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text(xy, text, font=ImageFont.truetype(CHALK, size), fill=color + (255,))
        a = np.array(layer.split()[3], np.float32) / 255
        a *= rnd.uniform(0.72, 1.0, a.shape)                      # 粉笔的颗粒
        layer.putalpha(Image.fromarray((a * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.6)))
        im.paste(layer, (0, 0), layer)

    fz = ImageFont.truetype(CHALK, 210)
    tw = ImageDraw.Draw(im).textlength("原LAI如此", font=fz)
    chalk("原LAI如此", 210, ((W - tw) / 2, 120), (0xF4, 0xF1, 0xE4))
    # 黄色粉笔波浪下划线
    pts = [(190 + i * 8, 400 + 7 * np.sin(i / 3.2)) for i in range(0, 87)]
    d.line(pts, fill="#F2C94C", width=7)
    sub = "像素讲解员的 AI 科普"
    fs = ImageFont.truetype(CHALK, 64)
    sw = ImageDraw.Draw(im).textlength(sub, font=fs)
    chalk(sub, 64, ((W - sw) / 2, 440), (0xF2, 0xC9, 0x4C))
    spr, _ = M.compose_sprite("wave_a_m0", eyes="idle_happy_m0")
    S = 7
    spr = spr.resize((64 * S, 64 * S), Image.NEAREST)
    im.paste(spr, ((W - 64 * S) // 2, 954 - 64 * S + 6), spr)
    return save(im, "yuanlai")


# ---------------------------------------------------------------- AI时代计算机专业研究生如何用AI
def cs():
    im = Image.new("RGB", (W, W), "#FFFFFF")
    d = ImageDraw.Draw(im)
    for y in range(30, W, 54):
        for x in range(30, W, 54):
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill="#E4E7EC")
    d.ellipse((520, 330, 1160, 970), fill="#DCEBFF")                  # 浅蓝圆
    orange = "#FF6A1A"
    cap = noto(40, 800)
    d.rounded_rectangle((70, 70, 70 + 560, 70 + 76), radius=38, outline=orange, width=5, fill="#FFFFFF")
    d.text((70 + 36, 70 + 12), "计算机专业 · AI 基础功", font=cap, fill=orange)
    f = noto(150, 900)
    d.text((70, 230), "AI时代计算机", font=f, fill="#111111")
    d.text((70, 230 + 160), "专业研究生", font=f, fill="#111111")
    hl = noto(190, 900)
    tw = d.textlength("如何用AI", font=hl)
    d.rectangle((60, 700 + 105, 60 + tw + 20, 700 + 165), fill="#FFE35C")           # 黄色荧光
    d.text((70, 700), "如何用AI", font=hl, fill=orange)
    return save(im, "cs")


# ---------------------------------------------------------------- Way to AGI
def way():
    im = Image.new("RGB", (W, W), "#FAF9F5")
    d = ImageDraw.Draw(im)
    orange = "#E8590C"
    d.text((90, 90), "Way to", font=noto(220, 900), fill="#141413")
    f = fit("AGI", 900, 860, 400)
    d.text((80, 300), "AGI", font=f, fill=orange)
    y = 880                                                              # 一条通向右边的路：粗线 + 箭头（在 AGI 下面，不压字）
    d.line((96, y, 860, y), fill="#141413", width=16)
    d.polygon([(850, y - 46), (850, y + 46), (960, y)], fill="#141413")
    d.text((96, 940), "悠一出镜 · AI 实战与思考", font=noto(52, 700), fill="#6B7280")
    return save(im, "way")


if __name__ == "__main__":
    ps = [openai(), yuanlai(), cs(), way()]
    ims = [Image.open(p).resize((540, 540), Image.LANCZOS) for p in ps]
    sheet = Image.new("RGB", (540 * 4 + 50, 560), "#888")
    for i, im in enumerate(ims):
        sheet.paste(im, (10 + i * 550, 10))
    sheet.save(r"C:\Users\yui\AppData\Local\Temp\claude\D----\7d19fe63-2954-44c3-99f1-13304adff1ba\scratchpad\series_covers_new.png")
    print("overview ok")
