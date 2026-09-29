"""Make Bilibili feed-style check images from a 1920x1080 cover.

usage: python check.py <cover.png> <out_prefix>
writes <out_prefix>_thumb320.png, _thumb480.png, _crop43.png, _crop43_thumb.png, _sheet.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = r"D:/大疆/AI科普/第01期_什么是API/制作/fonts/NotoSansSC.ttf"


def font(size, weight=500):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def feed_thumb(src, w, h):
    s = w / 320  # scale factor relative to 320 wide feed card
    im = src.resize((w, h), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # bottom gradient (B站 stats bar), ~ bottom 22% fading in
    gh = int(h * 0.26)
    for i in range(gh):
        a = int(170 * (i / gh) ** 1.3)
        d.line([(0, h - gh + i), (w, h - gh + i)], fill=(0, 0, 0, a))
    im = Image.alpha_composite(im, ov)
    d = ImageDraw.Draw(im)
    f = font(int(round(11 * s)), 500)
    pad = int(round(8 * s))
    d.text((pad, h - pad), "\u25B6 1.2万   \u2261 356", font=f, fill=(255, 255, 255, 255), anchor="ls")
    # duration pill, bottom-right
    txt = "06:02"
    tw = d.textlength(txt, font=f)
    ph = int(round(16 * s))
    pw = int(tw + 10 * s)
    x1, y1 = w - pad + int(2 * s), h - pad + int(4 * s)
    pill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([x1 - pw, y1 - ph, x1, y1], radius=int(4 * s), fill=(0, 0, 0, 150))
    im = Image.alpha_composite(im, pill)
    d = ImageDraw.Draw(im)
    d.text((x1 - pw / 2, y1 - ph / 2), txt, font=f, fill=(255, 255, 255, 255), anchor="mm")
    # rounded card corners like the feed
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=int(6 * s), fill=255)
    card = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    card.paste(im, (0, 0), mask)
    return card.convert("RGB")


def main():
    src = Image.open(sys.argv[1]).convert("RGB")
    assert src.size == (1920, 1080), src.size
    out = Path(sys.argv[2])
    t320 = feed_thumb(src, 320, 180)
    t480 = feed_thumb(src, 480, 270)
    t320.save(f"{out}_thumb320.png")
    t480.save(f"{out}_thumb480.png")
    crop = src.crop((240, 0, 1680, 1080))
    crop.save(f"{out}_crop43.png")
    c43t = crop.resize((240, 180), Image.LANCZOS)
    c43t.save(f"{out}_crop43_thumb.png")

    # review sheet: feed-like white page with several cards
    W, H = 1100, 700
    sheet = Image.new("RGB", (W, H), (246, 247, 248))
    d = ImageDraw.Draw(sheet)
    ft = font(14, 500)
    sheet.paste(t320, (20, 20))
    d.text((20, 206), "什么是API？“已接入DeepSeek”接的是什么？API Key怎么拿？｜原LAI如此 #01", font=ft, fill=(24, 25, 28))
    sheet.paste(t480, (360, 20))
    sheet.paste(src.crop((240, 0, 1680, 1080)).resize((360, 270), Image.LANCZOS), (860 - 120, 320))
    sheet.paste(c43t, (20, 320))
    d.text((20, 505), "4:3 @240x180", font=ft, fill=(90, 90, 90))
    d.text((740, 596), "4:3 crop @360x270", font=ft, fill=(90, 90, 90))
    # grayscale value check at 320
    g = t320.convert("L").convert("RGB")
    sheet.paste(g, (300, 320))
    d.text((300, 506), "grayscale 320", font=ft, fill=(90, 90, 90))
    sheet.save(f"{out}_sheet.png")
    print("ok", out)


if __name__ == "__main__":
    main()
