# -*- coding: utf-8 -*-
"""按给定秒数抽 1080p 代理的帧，叠 120 px 坐标网格（坐标 = 1920×1080 画面坐标），4 张拼成一张图，用来量裁切框。

  python gridframes.py out_prefix t1 t2 t3 ...        每 4 个时刻一张 out_prefix_1.png …（每格 960×540，右下角写秒数）
  python gridframes.py out_prefix --src 4k t1 ...      从 4K 原片抽（慢，坐标仍按 1920×1080 缩放后画）
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]


def grab(src, t, scale_w=1920):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", "-vf", f"scale={scale_w}:-1", "-f", "image2pipe", "-vcodec", "png", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    import io
    return Image.open(io.BytesIO(raw)).convert("RGB")


def main():
    args = sys.argv[1:]
    prefix = args.pop(0)
    src = HERE / "proxy_1080.mp4"
    if args and args[0] == "--src":
        args.pop(0)
        if args.pop(0) == "4k":
            src = EP.parents[1] / "素材" / "2026-10_ClaudeDesign设计师用法" / "原片_视频流.webm"   # 合集层素材
    times = [float(a) for a in args]
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
    big = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
    tiles = []
    for t in times:
        im = grab(src, t)
        d = ImageDraw.Draw(im, "RGBA")
        for x in range(0, 1920, 120):
            d.line([(x, 0), (x, 1080)], fill=(255, 0, 80, 110), width=1)
            d.text((x + 3, 2), str(x), fill=(255, 0, 80, 255), font=font)
        for y in range(0, 1080, 120):
            d.line([(0, y), (1920, y)], fill=(0, 120, 255, 110), width=1)
            d.text((3, y + 2), str(y), fill=(0, 120, 255, 255), font=font)
        d.rectangle([1700, 1010, 1920, 1080], fill=(0, 0, 0, 200))
        d.text((1712, 1018), f"{t:.1f}s", fill=(255, 220, 0), font=big)
        tiles.append(im.resize((960, 540), Image.LANCZOS))
    for k in range(0, len(tiles), 4):
        sheet = Image.new("RGB", (1920, 1080), (30, 30, 30))
        for j, tile in enumerate(tiles[k:k + 4]):
            sheet.paste(tile, ((j % 2) * 960, (j // 2) * 540))
        out = f"{prefix}_{k // 4 + 1}.png"
        sheet.save(out)
        print(out)


if __name__ == "__main__":
    main()
