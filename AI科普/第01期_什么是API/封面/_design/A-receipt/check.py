"""Make B-site feed thumbnail mockups (320x180, 480x270) and the centred 4:3 crop from a 1920x1080 still.

usage: python check.py <still.png> <out_prefix>
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = Path(r"D:/大疆/AI科普/第01期_什么是API/制作/fonts/NotoSansSC.ttf")


def font(px):
    f = ImageFont.truetype(str(FONT), px)
    try:
        f.set_variation_by_axes([500])
    except Exception:
        pass
    return f


def feed_thumb(src, w, h):
    im = src.resize((w, h), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # bottom gradient bar (play count / danmaku)
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
    # duration tag, bottom-right
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
    t320 = feed_thumb(src, 320, 180)
    t480 = feed_thumb(src, 480, 270)
    t320.save(pre + "_thumb320.png")
    t480.save(pre + "_thumb480.png")
    crop = src.crop((240, 0, 1680, 1080))
    crop.save(pre + "_crop43.png")
    # a 4:3 feed-size check too
    feed_thumb(crop, 320, 240).save(pre + "_crop43_thumb.png")
    # one review board: 320 at 2x (nearest, so the real pixels are visible) + 480 + 4:3 thumb
    board = Image.new("RGB", (640 + 24 + 480 + 24 + 320, 360 + 0), (40, 40, 40))
    board.paste(t320.resize((640, 360), Image.NEAREST), (0, 0))
    board.paste(t480, (664, 0))
    board.paste(feed_thumb(crop, 320, 240), (664 + 480 + 24, 0))
    board.save(pre + "_board.png")
    print("ok", pre)


if __name__ == "__main__":
    main()
