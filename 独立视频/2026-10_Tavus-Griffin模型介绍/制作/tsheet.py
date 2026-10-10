# -*- coding: utf-8 -*-
r"""带时间标签的联系表：每隔 step 秒取一帧，贴上秒数，拼成网格图。

  python tsheet.py <视频> --step 4 --cols 4 --w 480 --out <前缀> [--start 0] [--end 999] [--per 16]

最后一帧的秒数封顶在 时长 − 0.2 s（否则 ffmpeg 取不到）。每 per 帧一张图：<前缀>_1.png、<前缀>_2.png …
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = r"C:\Windows\Fonts\consola.ttf"


def duration(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--step", type=float, default=4.0)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=1e9)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--w", type=int, default=480)
    ap.add_argument("--per", type=int, default=16)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dur = duration(a.video)
    end = min(a.end, dur - 0.2)
    ts = []
    t = a.start
    while t <= end + 1e-6:
        ts.append(round(t, 2))
        t += a.step
    h = round(a.w * 9 / 16)
    font = ImageFont.truetype(FONT, 22)
    tmp = Path(tempfile.mkdtemp())
    frames = []
    for i, t in enumerate(ts):
        f = tmp / f"{i:04d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", a.video, "-frames:v", "1", "-vf", f"scale={a.w}:{h}:force_original_aspect_ratio=decrease,pad={a.w}:{h}:(ow-iw)/2:(oh-ih)/2", str(f)], check=True)
        im = Image.open(f).convert("RGB")
        d = ImageDraw.Draw(im)
        label = f"{t:.1f}s"
        d.rectangle([0, 0, 84, 28], fill=(0, 0, 0))
        d.text((4, 2), label, fill=(255, 255, 0), font=font)
        frames.append(im)
    n = 0
    for s in range(0, len(frames), a.per):
        chunk = frames[s:s + a.per]
        rows = (len(chunk) + a.cols - 1) // a.cols
        sheet = Image.new("RGB", (a.cols * a.w, rows * h), (30, 30, 30))
        for k, im in enumerate(chunk):
            sheet.paste(im, ((k % a.cols) * a.w, (k // a.cols) * h))
        n += 1
        out = f"{a.out}_{n}.png"
        sheet.save(out)
        print(out, f"{ts[s]:.1f}s–{ts[min(s + a.per, len(ts)) - 1]:.1f}s")


if __name__ == "__main__":
    main()
