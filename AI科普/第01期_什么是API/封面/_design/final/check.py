"""Bilibili feed mock-ups + 4:3 crop + greyscale / 160x90 checks for a 1920x1080 cover still.

usage: python check.py <still.png> <out_prefix> [<still_43.png>]
  still_43.png: optional dedicated 4:3 render (1920x1080 frame whose centre 1440 is the 4:3 cover)
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT = Path(r"D:/大疆/AI科普/第01期_什么是API/制作/fonts/NotoSansSC.ttf")


def font(px, wght=500):
    f = ImageFont.truetype(str(FONT), px)
    try:
        f.set_variation_by_axes([wght])
    except Exception:
        pass
    return f


def feed_thumb(src, w, h):
    """Downscale like the feed does, then overlay the stats gradient and the duration pill."""
    im = src.resize((w, h), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    gh = round(h * 0.22)
    for i in range(gh):
        a = int(170 * (i / gh) ** 1.3)
        d.line([(0, h - gh + i), (w, h - gh + i)], fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, ov)
    d = ImageDraw.Draw(im)
    fs = max(10, round(h * 0.068))
    f = font(fs)
    pad = round(w * 0.025)
    y = h - pad - fs
    d.text((pad, y - 1), "\u25B6 1.2万    \u25A4 356", font=f, fill=(255, 255, 255, 235))
    txt = "06:02"
    tw = d.textlength(txt, font=f)
    bw, bh = tw + fs * 0.9, fs * 1.45
    x1, y1 = w - pad, h - pad + 2
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([x1 - bw, y1 - bh, x1, y1], radius=round(fs * 0.3), fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, box)
    d = ImageDraw.Draw(im)
    d.text((x1 - bw + fs * 0.45, y1 - bh + fs * 0.12), txt, font=f, fill=(255, 255, 255, 240))
    return im.convert("RGB")


def main():
    src = Image.open(sys.argv[1]).convert("RGB")
    assert src.size == (1920, 1080), src.size
    pre = sys.argv[2]
    src43 = Image.open(sys.argv[3]).convert("RGB") if len(sys.argv) > 3 else src
    crop = src43.crop((240, 0, 1680, 1080))
    t320 = feed_thumb(src, 320, 180)
    t480 = feed_thumb(src, 480, 270)
    t160 = src.resize((160, 90), Image.LANCZOS)
    c320 = feed_thumb(crop, 320, 240)
    t320.save(pre + "_thumb320.png")
    t480.save(pre + "_thumb480.png")
    crop.save(pre + "_crop43.png")
    c320.save(pre + "_crop43_thumb.png")

    # board 1: 320 feed at 2x nearest (real pixels visible) + 480 + 4:3 320x240
    board = Image.new("RGB", (640 + 24 + 480 + 24 + 320, 360), (40, 40, 40))
    board.paste(t320.resize((640, 360), Image.NEAREST), (0, 0))
    board.paste(t480, (664, 0))
    board.paste(c320, (664 + 480 + 24, 0))
    board.save(pre + "_board.png")

    # board 2: greyscale 320, 160x90 (x2 nearest), 4:3 crop greyscale
    g = Image.new("RGB", (640 + 24 + 320 + 24 + 320, 360), (40, 40, 40))
    g.paste(ImageOps.grayscale(t320).convert("RGB").resize((640, 360), Image.NEAREST), (0, 0))
    g.paste(t160.resize((320, 180), Image.NEAREST), (664, 0))
    g.paste(t160, (664, 200))
    g.paste(ImageOps.grayscale(c320).convert("RGB"), (664 + 320 + 24, 0))
    g.save(pre + "_board2.png")
    print("ok", pre)


if __name__ == "__main__":
    main()
