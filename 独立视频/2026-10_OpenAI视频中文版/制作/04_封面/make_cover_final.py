# -*- coding: utf-8 -*-
"""封面 A3（现行）：用户选了方案 A。要求依次是：① 配色用 OpenAI 的蓝 / 白 / 黑  ② 去掉“演示翻车了”，只留“OpenAI 重新演示 dots”
③ 取消蓝色渐变，蓝色只作“OpenAI 重新演示”几个字的外部勾线。

  python make_cover_final.py

照片保持原色；底部只有 A 原来的黑色压暗（让白字清楚）。“OpenAI 重新演示”= 白字 + OpenAI 蓝外勾线；“dots”= 黑色圆角块 + 白字；底部小字 = 白底黑字。
蓝色取自 openai.com 页面自己的品牌蓝色阶（CSS 变量 --color-brand-blue-*）：#3A83F7（400，勾线用）/ #2C67C5（500）/ #1F4E94（600）；黑 #080808；白 #FFFFFF。
出 16:9（1920×1080）和 4:3（1440×1080）。
"""
from PIL import Image, ImageDraw, ImageFilter

from make_cover3 import HERE, fit, font, load, tw

BLUE = (58, 131, 247)
BLACK, WHITE = (8, 8, 8), (255, 255, 255)
TAG = "DevDay 2026｜订机票 · 选酒店 · 整理用户反馈｜中文同传"


def black_shade(img, y0):
    """从 y0 往下渐渐压暗（和方案 A 一样），只用黑色。"""
    W, H = img.size
    y0 = int(y0)                                  # 起点取整，否则 y0 是小数时第一行会出现负数的 0.9 次方
    g = Image.new("L", (1, H), 0)
    for y in range(y0, H):
        g.putpixel((0, y), int(225 * ((y - y0) / (H - y0)) ** 0.9))
    return Image.composite(Image.new("RGBA", (W, H), (6, 8, 12, 255)), img, g.resize((W, H)))


def blue_outlined_text(img, xy, text, f, anchor, stroke):
    """白字 + 蓝色外勾线：先垫一层柔和的暗影，再画蓝色（字 + 描边），最后在上面盖白字。"""
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 8), text, font=f, fill=(0, 0, 0, 120), stroke_width=stroke, stroke_fill=(0, 0, 0, 120), anchor=anchor)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    bl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(bl).text(xy, text, font=f, fill=BLUE + (255,), stroke_width=stroke, stroke_fill=BLUE + (255,), anchor=anchor)
    img.alpha_composite(bl)
    ImageDraw.Draw(img).text(xy, text, font=f, fill=WHITE, anchor=anchor)


def pill_word(img, x, base, size, text):
    """黑色圆角块 + 白字，文字按基线对齐；返回右边界。"""
    d = ImageDraw.Draw(img)
    f = font(size, 900)
    w = tw(d, text, f)
    padx = size * 0.30
    d.rounded_rectangle((int(x), int(base - size * 0.98), int(x + w + 2 * padx), int(base + size * 0.24)), radius=int(size * 0.34), fill=BLACK)
    d.text((x + padx, base), text, font=f, fill=WHITE, anchor="ls")
    return x + w + 2 * padx


def draw_tag(img, W, s, y):
    d = ImageDraw.Draw(img)
    f = font(40 * s, 700)
    w = tw(d, TAG, f)
    pad = 30 * s
    d.rounded_rectangle((int((W - w) / 2 - pad), int(y), int((W + w) / 2 + pad), int(y + 72 * s)), radius=int(36 * s), fill=WHITE)
    d.text((W / 2, y + 36 * s), TAG, font=f, fill=BLACK, anchor="mm")


def make(W, H):
    wide = W / H > 1.5
    img = fit(load("g_4.6.png"), W, H, cx=0.5 if wide else 0.0, cy=0.3).convert("RGBA")
    img = black_shade(img, H * (0.44 if wide else 0.40))
    if wide:                                       # 一行：“OpenAI 重新演示”（白字蓝勾线）+ 黑块“dots”
        size, stroke = 150, 15
        f = font(size, 900)
        left = "OpenAI 重新演示"
        d = ImageDraw.Draw(img)
        wl, wd = tw(d, left, f), tw(d, "dots", f) + 2 * size * 0.30
        gap = size * 0.26
        x = (W - (wl + gap + wd)) / 2
        base = H * 0.725
        blue_outlined_text(img, (x, base), left, f, "ls", stroke)
        pill_word(img, x + wl + gap, base, size, "dots")
        draw_tag(img, W, 1.0, H * 0.862)
    else:                                          # 两行：上面“OpenAI 重新演示”，下面大的黑块“dots”
        size, stroke = 138, 13
        f = font(size, 900)
        base1 = H * 0.640
        blue_outlined_text(img, (W / 2, base1), "OpenAI 重新演示", f, "ms", stroke)
        size2 = 168
        d = ImageDraw.Draw(img)
        w2 = tw(d, "dots", font(size2, 900)) + 2 * size2 * 0.30
        pill_word(img, (W - w2) / 2, base1 + size2 * 1.18, size2, "dots")
        draw_tag(img, W, 0.85, H * 0.872)
    return img.convert("RGB")


def main():
    for tag, (w, h) in (("16x9", (1920, 1080)), ("4x3", (1440, 1080))):
        out = HERE / f"封面_A3_{tag}.png"
        make(w, h).save(out)
        print(out.name)


if __name__ == "__main__":
    main()
