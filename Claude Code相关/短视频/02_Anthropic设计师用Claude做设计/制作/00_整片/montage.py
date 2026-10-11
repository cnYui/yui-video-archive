# -*- coding: utf-8 -*-
"""把 build/stills[_tag]/*.png 拼成总览图（每张 6 列，缩到 360×780），写到 build/montage[_tag]_N.png；看版面用，字要看就单独打开 stills 里的原图。

  python montage.py [tag]        # 例：python montage.py v2 → 读 build/stills_v2/
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BUILD = Path(__file__).resolve().parent / "build"


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else ""
    folder = BUILD / (f"stills_{tag}" if tag else "stills")
    fs = sorted(folder.glob("t*.png"))
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    tw, th = 360, 780
    for k in range(0, len(fs), 6):
        chunk = fs[k: k + 6]
        im = Image.new("RGB", (tw * len(chunk) + 6 * (len(chunk) - 1), th), (30, 30, 30))
        d = ImageDraw.Draw(im)
        for i, f in enumerate(chunk):
            x = i * (tw + 6)
            im.paste(Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS), (x, 0))
            d.rectangle([x, 0, x + 88, 28], fill=(0, 0, 0))
            d.text((x + 5, 3), f.stem[1:] + "s", fill=(255, 220, 0), font=font)
        out = BUILD / f"montage{'_' + tag if tag else ''}_{k // 6 + 1}.png"
        im.save(out)
        print(out)


if __name__ == "__main__":
    main()
