# -*- coding: utf-8 -*-
"""画静态层：build/bg.png（米白底 + 淡点阵 + 标题 + 上下两个外框）、build/mask_inner.png（框里画面的圆角蒙版）、build/fg.png（盖在画面上的来源角标）。

  python make_bg.py

版式数字全部来自 config.py（照技能 short-video 的 layout.md / 引擎 index.html 的 CSS）。标题取 台本/录制稿.json 的 hook（两行）和 kicker。
字体：Noto Sans SC 变量字体（标题 900 / 800 / 700 字重）。
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import config as C

BUILD = C.HERE / "build"
SS = 4                                        # 圆角、点阵用 4 倍超采样画


def vfont(px, weight):
    f = ImageFont.truetype(str(C.VAR_FONT), px)
    f.set_variation_by_axes([weight])
    return f


def rounded_mask(w, h, r, ss=SS):
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def draw_dots(img):
    """radial-gradient(circle at 1px 1px, rgba(20,20,19,.07) 1.4px, transparent 1.6px) 0 0 / 36px 36px"""
    layer = Image.new("L", (C.W * 2, C.H * 2), 0)
    d = ImageDraw.Draw(layer)
    for gy in range(0, C.H + 36, 36):
        for gx in range(0, C.W + 36, 36):
            cx, cy = (gx + 1) * 2, (gy + 1) * 2
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=255)
    layer = layer.resize((C.W, C.H), Image.LANCZOS).point(lambda v: int(v * 0.07))
    img.paste(Image.new("RGB", (C.W, C.H), (20, 20, 19)), (0, 0), layer)


def draw_box(img, y):
    """外框：白底 + 1 px 边 + 圆角 + 阴影（0 18px 44px rgba(0,0,0,.16)），里面铺 #EEF0F3 当画面没盖住时的底。"""
    x, w, h = C.BOX_X, C.BOX_W, C.BOX_H
    shadow = Image.new("L", (C.W, C.H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle([x, y + 18, x + w - 1, y + 18 + h - 1], radius=C.RADIUS, fill=255)
    shadow = shadow.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.16))
    img.paste(Image.new("RGB", (C.W, C.H), (0, 0, 0)), (0, 0), shadow)
    border = rounded_mask(w, h, C.RADIUS)
    img.paste(Image.new("RGB", (w, h), C.LINE), (x, y), border)
    inner_outer = rounded_mask(w - 2, h - 2, C.RADIUS - 1)
    img.paste(Image.new("RGB", (w - 2, h - 2), C.WHITE), (x + 1, y + 1), inner_outer)
    img.paste(Image.new("RGB", (C.INNER_W, C.INNER_H), (0xEE, 0xF0, 0xF3)), (x + C.PAD, y + C.PAD), rounded_mask(C.INNER_W, C.INNER_H, C.INNER_RADIUS))


def text_spaced(d, cx, cy, s, font, fill, spacing):
    """字间距（CSS letter-spacing）：逐字画，整体居中；返回总宽。"""
    widths = [font.getlength(ch) for ch in s]
    total = sum(widths) + spacing * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        d.text((x, cy), ch, font=font, fill=fill, anchor="lm")
        x += w + spacing
    return total


def draw_title(img, hook, kicker):
    d = ImageDraw.Draw(img)
    # kicker：30 px / 700，字间距 .18em；<b> 里的词用强调橙 800
    parts = re.split(r"(<b>.*?</b>)", kicker)
    segs = []
    for p in parts:
        if not p:
            continue
        if p.startswith("<b>"):
            segs.append((p[3:-4], vfont(30, 800), C.ORANGE))
        else:
            segs.append((p, vfont(30, 700), C.GREY))
    sp = 30 * 0.18
    total = sum(f.getlength(ch) + sp for s, f, _ in segs for ch in s) - sp
    x = C.W / 2 - total / 2
    ky = 280 + 22
    for s, f, col in segs:
        for ch in s:
            d.text((x, ky), ch, font=f, fill=col, anchor="lm")
            x += f.getlength(ch) + sp
    # 第一行：黑 76 px / 900；第二行：橙 60 px / 800，带黄荧光
    t1y = 280 + 43 + 22 + 46
    d.text((C.W / 2, t1y), hook[0], font=vfont(76, 900), fill=C.INK, anchor="mm")
    f2 = vfont(60, 800)
    t2_top = 280 + 43 + 22 + 93 + 10
    w2 = f2.getlength(hook[1])
    box_h = 75
    d.rectangle([C.W / 2 - w2 / 2 - 6, t2_top + box_h * 0.62, C.W / 2 + w2 / 2 + 6, t2_top + box_h * 0.94], fill=C.MARKER)
    d.text((C.W / 2, t2_top + box_h / 2), hook[1], font=f2, fill=C.ORANGE, anchor="mm")
    return {"kicker_w": round(total), "t1_w": round(vfont(76, 900).getlength(hook[0])), "t2_w": round(w2)}


def make_fg():
    """来源角标（引擎的 .credit：黑底 .86、白字 700、圆角），放在上框右上角（画面里是房间的墙，不挡内容）。"""
    fg = Image.new("RGBA", (C.W, C.H), (0, 0, 0, 0))
    d = ImageDraw.Draw(fg)
    f = vfont(24, 700)
    text = "来源 · Claude 官方 YouTube"
    tw = f.getlength(text)
    ph, pw = 44, tw + 34
    right = C.BOX_X + C.PAD + C.INNER_W - 14
    x1, y0 = right - pw, C.FACE_Y + C.PAD + 13
    pill = Image.new("L", (int(pw) * SS, ph * SS), 0)
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, int(pw) * SS - 1, ph * SS - 1], radius=11 * SS, fill=int(255 * 0.86))
    pill = pill.resize((int(pw), ph), Image.LANCZOS)
    fg.paste(Image.new("RGBA", (int(pw), ph), (17, 17, 17, 255)), (int(x1), y0), pill)
    d.text((x1 + pw / 2, y0 + ph / 2 + 1), text, font=f, fill=(255, 255, 255, 255), anchor="mm")
    return fg


def main():
    BUILD.mkdir(exist_ok=True)
    sc = json.loads((C.EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    img = Image.new("RGB", (C.W, C.H), C.BG)
    draw_dots(img)
    draw_box(img, C.FACE_Y)
    draw_box(img, C.SCREEN_Y)
    info = draw_title(img, sc["hook"], sc["kicker"])
    img.save(BUILD / "bg.png")
    rounded_mask(C.INNER_W, C.INNER_H, C.INNER_RADIUS).save(BUILD / "mask_inner.png")
    make_fg().save(BUILD / "fg.png")
    print("bg.png / mask_inner.png / fg.png 已写到", BUILD, info)
    for k, w in (("标题第一行", info["t1_w"]), ("标题第二行", info["t2_w"]), ("kicker", info["kicker_w"])):
        if w > C.W - 80:
            print(f"⚠ {k} 宽 {w} px，超过 {C.W - 80}")


if __name__ == "__main__":
    main()
