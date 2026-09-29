"""Export the final cover PNGs + one preview board.

usage: python export.py <still_16x9.png>
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from check import feed_thumb, font  # noqa: E402

OUT = Path(r"D:/大疆/AI科普/第01期_什么是API/封面")


def main():
    src = Image.open(sys.argv[1]).convert("RGB")
    assert src.size == (1920, 1080)
    p169 = OUT / "封面_16x9_1920x1080.png"
    p43 = OUT / "封面_4x3_1440x1080.png"
    src.save(p169, optimize=True)
    crop = src.crop((240, 0, 1680, 1080))
    crop.save(p43, optimize=True)

    # preview board
    BG, FG, DIM = (30, 30, 32), (235, 233, 227), (150, 147, 140)
    M, G = 40, 36
    big_w, big_h = 1152, 648            # 16:9 at 0.6
    s43_w, s43_h = 864, 648             # 4:3 at 0.6
    W = M + big_w + G + s43_w + M
    t320 = feed_thumb(src, 320, 180)
    t480 = feed_thumb(src, 480, 270)
    c320 = feed_thumb(crop, 320, 240)
    row2_h = 360
    H = M + 44 + big_h + G + 44 + row2_h + M
    board = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(board)
    fh, fs = font(28, 700), font(22, 500)

    def label(x, y, title, note):
        d.text((x, y), title, font=fh, fill=FG)
        d.text((x + d.textlength(title, font=fh) + 16, y + 5), note, font=fs, fill=DIM)

    y0 = M
    label(M, y0, "16:9 封面", "1920×1080 · 封面_16x9_1920x1080.png")
    board.paste(src.resize((big_w, big_h), Image.LANCZOS), (M, y0 + 44))
    x43 = M + big_w + G
    label(x43, y0, "4:3 封面", "1440×1080 · 居中裁切")
    board.paste(crop.resize((s43_w, s43_h), Image.LANCZOS), (x43, y0 + 44))

    y1 = y0 + 44 + big_h + G
    x = M
    label(x, y1, "信息流 320×180", "实际像素")
    board.paste(t320, (x, y1 + 44))
    x += 320 + G
    label(x, y1, "320×180 ×2", "最近邻放大，看清实际像素")
    board.paste(t320.resize((640, 360), Image.NEAREST), (x, y1 + 44))
    x += 640 + G
    label(x, y1, "信息流 480×270", "")
    board.paste(t480, (x, y1 + 44))
    x += 480 + G
    label(x, y1, "4:3 · 320×240", "")
    board.paste(c320, (x, y1 + 44))
    need_w = x + 320 + M
    if need_w > W:  # widen if the bottom row overflows
        wide = Image.new("RGB", (need_w, H), BG)
        wide.paste(board, (0, 0))
        board = wide
    board.save(OUT / "封面_预览.png", optimize=True)

    for pth in (p169, p43, OUT / "封面_预览.png"):
        im = Image.open(pth)
        print(pth.name, im.size, f"{pth.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == "__main__":
    main()
