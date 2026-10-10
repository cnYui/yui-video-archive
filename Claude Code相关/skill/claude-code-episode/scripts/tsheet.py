# -*- coding: utf-8 -*-
"""联系表：把视频按 fps 抽帧，每帧左上角贴秒数，拼成一张图（看素材 / 抽查成片用）。

  python tsheet.py <视频> <输出.png> [fps=1] [cols=5] [thumb_w=480] [t0=0] [t1=到结尾]
例：python tsheet.py demo.mp4 sheet.png 1 5 480            整条每秒一帧
    python tsheet.py demo.mp4 w.png 4 5 384 12 14.5         第 12–14.5 秒每秒 4 帧（看某个瞬间什么时候出现）
"""
import subprocess, sys, tempfile, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 5
tw = int(sys.argv[5]) if len(sys.argv) > 5 else 480
t0 = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", src], capture_output=True, text=True).stdout.strip())
t1 = float(sys.argv[7]) if len(sys.argv) > 7 else dur
tmp = Path(tempfile.mkdtemp())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t0), "-t", str(t1 - t0), "-i", src, "-vf", f"fps={fps},scale={tw}:-1", "-q:v", "3", str(tmp / "f_%04d.jpg")], check=True)
fs = sorted(tmp.glob("f_*.jpg"))
ims = [Image.open(f) for f in fs]
w, h = ims[0].size
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (20, 20, 20))
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)
except Exception:
    font = ImageFont.load_default()
d = ImageDraw.Draw(sheet)
for i, im in enumerate(ims):
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(im, (x, y))
    tt = t0 + i / fps
    d.rectangle([x + 4, y + 4, x + 118, y + 36], fill=(0, 0, 0))
    d.text((x + 10, y + 6), f"{tt:6.1f}s", fill=(255, 220, 0), font=font)
sheet.save(out)
shutil.rmtree(tmp, ignore_errors=True)
print(out, sheet.size, len(ims), "frames")
