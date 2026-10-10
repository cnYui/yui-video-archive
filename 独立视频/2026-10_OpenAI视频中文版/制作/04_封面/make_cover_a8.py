# -*- coding: utf-8 -*-
"""封面 A8：A7 的黑块“OpenAI”改成和下面那行一样大的字，去掉黑色背景，只留黑色外边框（像字幕：白字 + 黑边）。
用户原话：“openAI字大一点，和下面文字一样字号，然后你把OpenAI黑色背景去除，保留字幕外边框是黑色的就像”
（话停在“就像”，我按“像字幕那样：白字 + 黑色外边框”理解）。

  python make_cover_a8.py     # 出 封面_A8_*（“。。”）和 封面_A8_省略号_*（“……”）各 16:9 / 4:3

版面：两行居中，字号一样（16:9 是 150，4:3 是 138）——“OpenAI”白字黑边 / “公开演示翻车后。。”白字蓝边；其余（照片上移、压暗、官方 dots 角色）和 A6 / A7 一样。
“OpenAI”里的 p 会往下伸，两行间距比 A5 的 1.18 倍大一点（1.30），免得 p 的黑边碰到下一行的字。
"""
from PIL import Image, ImageDraw, ImageFilter

from make_cover3 import HERE, fit, font, load
from make_cover_a4 import clean_laptop_sticker, dots_group, put, shift_up
from make_cover_a6 import ink_span
from make_cover_final import BLACK, WHITE, black_shade, blue_outlined_text

KICKER = "OpenAI"
HOOK = "公开演示翻车后"


def black_outlined_text(img, xy, text, f, anchor, stroke):
    """白字 + 黑色外边框（像字幕）：先垫一层柔和的暗影，再画黑色（字 + 描边），最后在上面盖白字。"""
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0], xy[1] + 8), text, font=f, fill=(0, 0, 0, 120), stroke_width=stroke, stroke_fill=(0, 0, 0, 120), anchor=anchor)
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    bk = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(bk).text(xy, text, font=f, fill=BLACK + (255,), stroke_width=stroke, stroke_fill=BLACK + (255,), anchor=anchor)
    img.alpha_composite(bk)
    ImageDraw.Draw(img).text(xy, text, font=f, fill=WHITE, anchor=anchor)


def make(W, H, tail, size, b1, gap=1.30, dy=80, gw=1000):
    wide = W / H > 1.5
    stroke = round(size * 0.10)
    img = fit(clean_laptop_sticker(load("g_4.6.png")), W, H, cx=0.5 if wide else 0.0, cy=0.3).convert("RGBA")
    img = shift_up(img, dy)
    img = black_shade(img, H * 0.42)
    f = font(size, 900)
    l, r = ink_span(f, KICKER, stroke)
    black_outlined_text(img, ((W - (r - l)) / 2 - l, b1), KICKER, f, "ls", stroke)
    text = HOOK + tail
    l, r = ink_span(f, text, stroke)
    blue_outlined_text(img, ((W - (r - l)) / 2 - l, b1 + gap * size), text, f, "ls", stroke)
    grp = dots_group(gw)
    put(img, grp, (W - grp.width) / 2, H - grp.height + 8)
    return img.convert("RGB")


CFG = {"16x9": dict(W=1920, H=1080, size=150, b1=542),
       "4x3": dict(W=1440, H=1080, size=138, b1=556)}


def main():
    for name, tail in (("", "。。"), ("省略号_", "……")):
        for tag, c in CFG.items():
            out = HERE / f"封面_A8_{name}{tag}.png"
            make(tail=tail, **c).save(out)
            print(out.name)


if __name__ == "__main__":
    main()
