"""Make B站 feed-thumbnail simulations and a 4:3 centre crop from a rendered 1920x1080 cover.

usage: python check.py <still.png> <out_prefix>
writes <out_prefix>_thumb320.png, _thumb480.png, _crop43.png, _sheet.png
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT = "D:/大疆/AI科普/第01期_什么是API/制作/fonts/NotoSansSC.ttf"


def font(size, weight=500):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def feed_thumb(src, w, h):
    im = src.resize((w, h), Image.LANCZOS).convert("RGBA")
    s = w / 320
    # bottom gradient (stats bar)
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    gh = int(h * 0.28)
    for y in range(gh):
        a = int(170 * (y / gh) ** 1.3)
        gd.line([(0, h - gh + y), (w, h - gh + y)], fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, grad)
    d = ImageDraw.Draw(im)
    f = font(int(11 * s), 500)
    # stats (left bottom)
    d.text((int(8 * s), h - int(18 * s)), "▶ 1.2万   ▤ 356", font=f, fill=(255, 255, 255, 235))
    # duration badge (right bottom)
    txt = "06:02"
    tb = d.textbbox((0, 0), txt, font=f)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    pad_x, pad_y = int(5 * s), int(3 * s)
    bx1 = w - int(6 * s)
    by1 = h - int(6 * s)
    bx0 = bx1 - tw - 2 * pad_x
    by0 = by1 - th - 2 * pad_y - int(2 * s)
    badge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(badge).rounded_rectangle([bx0, by0, bx1, by1], radius=int(4 * s), fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, badge)
    d = ImageDraw.Draw(im)
    d.text((bx0 + pad_x - tb[0], by0 + pad_y - tb[1] + int(1 * s)), txt, font=f, fill=(255, 255, 255, 255))
    # rounded card corners like the feed
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(6 * s), fill=255)
    out = Image.new("RGBA", (w, h), (246, 247, 248, 255))
    out.paste(im, (0, 0), mask)
    return out.convert("RGB")


def main():
    src = Image.open(sys.argv[1]).convert("RGB")
    assert src.size == (1920, 1080), src.size
    pre = Path(sys.argv[2])
    t320 = feed_thumb(src, 320, 180)
    t480 = feed_thumb(src, 480, 270)
    crop = src.crop((240, 0, 1680, 1080))
    t320.save(f"{pre}_thumb320.png")
    t480.save(f"{pre}_thumb480.png")
    crop.save(f"{pre}_crop43.png")
    # review sheet: feed row mock (white page) + 4:3 small
    sheet = Image.new("RGB", (1500, 620), (246, 247, 248))
    sheet.paste(t320, (20, 20))
    sheet.paste(t480, (360, 20))
    sheet.paste(src.resize((480, 270), Image.LANCZOS), (860, 20))
    c43 = crop.resize((360, 270), Image.LANCZOS)
    sheet.paste(c43, (20, 320))
    sheet.paste(crop.resize((240, 180), Image.LANCZOS), (400, 320))
    # 4:3 at small size with badge
    sheet.paste(feed_thumb(crop.resize((1440, 1080)), 240, 180), (660, 320))
    sheet.save(f"{pre}_sheet.png")
    print("ok", pre)


if __name__ == "__main__":
    main()
