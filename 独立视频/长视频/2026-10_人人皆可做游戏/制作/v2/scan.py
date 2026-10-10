# -*- coding: utf-8 -*-
"""scan.py —— 从实况录像（A–E 段）里按间隔抽帧拼联系表，找镜头用。
  python scan.py B 253 330 2 _check/b_katsura.png [列数]"""
import io
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

REC = Path(r"D:\大疆\游戏素材\银魂\录屏素材\2026-10-06_全流程实况")
SRC = {"A": "A_序章到第三章", "B": "B_第四到第七章", "C": "C_第八到第十章", "D": "D_第十一章到终章", "E": "E_序章输一次重来"}


def main():
    ch, t0, t1, step, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    cols = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    src = REC / SRC[ch] / "full.webm"
    ims = []
    t = t0
    while t <= t1 + 1e-6:
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.2f" % t, "-i", str(src), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
        if r.stdout:
            ims.append((t, Image.open(io.BytesIO(r.stdout)).convert("RGB")))
        t += step
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 388 + 4, rows * 220 + 4), (20, 20, 20))
    d = ImageDraw.Draw(sh)
    for i, (t, im) in enumerate(ims):
        x, y = 2 + (i % cols) * 388, 2 + (i // cols) * 220
        sh.paste(im, (x, y))
        d.text((x + 4, y + 2), "%g" % t, fill=(255, 255, 0))
    sh.save(out)
    print(out, len(ims))


main()
