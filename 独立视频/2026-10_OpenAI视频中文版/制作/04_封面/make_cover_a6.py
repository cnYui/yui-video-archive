# -*- coding: utf-8 -*-
"""封面 A6：A5 的文字再缩减。用户原话：“封面文字继续缩减，修改为：  DevDay公开演示翻车后。。”

  python make_cover_a6.py     # 出 封面_A6_*（“。。”照用户打的原样）和 封面_A6_省略号_*（“……”）各 16:9 / 4:3

“。。”我读不准：可能就是两个句号（也像两个 dots），也可能是想打省略号“……”，所以两种都出，A6 = 原样。
版面：两行居中——黑块“DevDay”（和 A3–A5 里黑块“dots”同一个样式）/ 大一点的白字蓝勾线“公开演示翻车后。。”，下面还是官方 dots 四只角色。
“。”在字体里是贴着格子左下角的小圈，按字格居中会显得整行偏左，所以第二行按墨迹宽度居中。
"""
from PIL import Image, ImageDraw

from make_cover3 import HERE, fit, font, load, tw
from make_cover_a4 import clean_laptop_sticker, dots_group, put, shift_up
from make_cover_final import black_shade, blue_outlined_text, pill_word

KICKER = "DevDay"
HOOK = "公开演示翻车后"


def ink_span(f, text, stroke):
    """真实墨迹（含描边）相对于起笔点 x 的左、右边界：在草稿图上画一次再量。
    textbbox 对“。”这种贴着格子左下角的小圈估得不准（第一版整行偏左了约 40 px）。"""
    pad = int(f.size)
    im = Image.new("L", (pad * (len(text) + 3), pad * 2), 0)
    ImageDraw.Draw(im).text((pad, int(pad * 1.4)), text, font=f, fill=255, stroke_width=stroke, anchor="ls")
    l, _, r, _ = im.getbbox()
    return l - pad, r - pad


def make(W, H, tail, size1, size2, b1, dy=80, gw=1000):
    wide = W / H > 1.5
    stroke = round(size2 * 0.10)
    img = fit(clean_laptop_sticker(load("g_4.6.png")), W, H, cx=0.5 if wide else 0.0, cy=0.3).convert("RGBA")
    img = shift_up(img, dy)
    img = black_shade(img, H * 0.42)
    d = ImageDraw.Draw(img)
    f1, f2 = font(size1, 900), font(size2, 900)
    w1 = tw(d, KICKER, f1) + 2 * size1 * 0.30                   # 黑块宽度（pill_word 里的算法）
    pill_word(img, (W - w1) / 2, b1, size1, KICKER)
    b2 = b1 + 0.24 * size1 + 20 + stroke + 0.88 * size2         # 黑块底边 + 间隙 + 描边 + 字高
    text = HOOK + tail
    l, r = ink_span(f2, text, stroke)
    blue_outlined_text(img, ((W - (r - l)) / 2 - l, b2), text, f2, "ls", stroke)
    grp = dots_group(gw)
    put(img, grp, (W - grp.width) / 2, H - grp.height + 8)
    return img.convert("RGB")


CFG = {"16x9": dict(W=1920, H=1080, size1=104, size2=150, b1=535),
       "4x3": dict(W=1440, H=1080, size1=104, size2=138, b1=549)}


def main():
    for name, tail in (("", "。。"), ("省略号_", "……")):
        for tag, c in CFG.items():
            out = HERE / f"封面_A6_{name}{tag}.png"
            make(tail=tail, **c).save(out)
            print(out.name)


if __name__ == "__main__":
    main()
