"""Generate the show's own backgrounds (no third-party images): blue pixel-style 1920x1080 PNGs -> SERIES/素材/背景图库/.

    python gen_backgrounds.py [--series D:/大疆/AI日报]

Deterministic (fixed seeds), so re-running gives the same files. Existing files are not overwritten unless --force.
The engine draws them at episode.json bg_alpha / bg_blur over navy #1B2340, so keep them calm and dark.
"""
import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

W, H, PX = 1920, 1080, 8          # PX = size of one "pixel" block


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(0, H, PX):     # banded in PX steps: a pixel-art gradient, not a smooth one
        d.rectangle([0, y, W, y + PX], fill=lerp(top, bottom, y / H))
    return img


def deep_sea(seed=11):
    rnd = random.Random(seed)
    img = gradient((10, 20, 48), (26, 60, 118))
    d = ImageDraw.Draw(img, "RGBA")
    for i in range(7):            # light shafts from the top-left
        x0 = 120 + i * 230 + rnd.randint(-40, 40)
        d.polygon([(x0, 0), (x0 + 90, 0), (x0 + 420, H), (x0 + 260, H)], fill=(150, 200, 255, 10))
    for _ in range(140):          # rising bubbles: hollow pixel squares
        x = rnd.randrange(0, W // PX) * PX
        y = rnd.randrange(0, H // PX) * PX
        s = rnd.choice([1, 1, 1, 2, 2, 3]) * PX
        a = rnd.randint(22, 60)
        d.rectangle([x, y, x + s, y + s], outline=(198, 230, 251, a), width=2 if s > PX else 1)
    return img


def star_dots(seed=23):
    rnd = random.Random(seed)
    img = gradient((12, 18, 44), (22, 38, 84))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(260):
        x = rnd.randrange(0, W // PX) * PX
        y = rnd.randrange(0, H // PX) * PX
        c = rnd.choice([(151, 195, 240), (198, 230, 251), (243, 201, 140)])
        d.rectangle([x, y, x + PX - 1, y + PX - 1], fill=c + (rnd.randint(30, 90),))
        if rnd.random() < 0.12:   # a few 4-point sparkles
            for dx, dy in ((PX, 0), (-PX, 0), (0, PX), (0, -PX)):
                d.rectangle([x + dx, y + dy, x + dx + PX - 1, y + dy + PX - 1], fill=c + (40,))
    return img


def waves(seed=37):
    rnd = random.Random(seed)
    img = gradient((14, 24, 56), (20, 52, 104))
    d = ImageDraw.Draw(img, "RGBA")
    for band in range(9):
        y0 = 420 + band * 72
        amp = 10 + band * 3
        ph = rnd.random() * math.tau
        col = lerp((74, 136, 218), (151, 195, 240), band / 8) + (18 + band * 4,)
        for x in range(0, W, PX):
            y = y0 + int(amp * math.sin(x / 140 + ph)) // PX * PX
            d.rectangle([x, y, x + PX - 1, y + PX * 2 - 1], fill=col)
    return img


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--series", default=r"D:/大疆/AI日报")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    out = Path(args.series) / "素材" / "背景图库"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("01_深海气泡.png", deep_sea), ("02_星点.png", star_dots), ("03_波纹.png", waves)):
        p = out / name
        if p.exists() and not args.force:
            print("keep", p)
            continue
        fn().save(p, optimize=True)
        print("wrote", p)


if __name__ == "__main__":
    main()
