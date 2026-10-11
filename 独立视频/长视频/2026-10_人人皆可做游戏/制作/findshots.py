"""从实况录像（384×216 webm）里按时间段抽联系表，找镜头用：python findshots.py A 100 160 1 out.png [列数]
A/B/C/D = 实况录像的段；时间是这一段 webm 自己的时间轴。"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REC = Path(r"D:\大疆\游戏素材\银魂\录屏素材\2026-10-06_全流程实况")
DIRS = {"A": "A_序章到第三章", "B": "B_第四到第七章", "C": "C_第八到第十章", "D": "D_第十一章到终章"}
k, a, b, step, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
cols = int(sys.argv[6]) if len(sys.argv) > 6 else 8
W, H = 384, 216
raw = subprocess.run(["ffmpeg", "-v", "error", "-threads", "2", "-ss", "%.3f" % a, "-t", "%.3f" % (b - a + 0.05), "-i", str(REC / DIRS[k] / "full.webm"),
                      "-vf", "fps=%g" % (1 / step), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
n = len(raw) // (W * H * 3)
font = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 14)
rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (cols * (W + 4), rows * (H + 4)), (20, 20, 24))
for i in range(n):
    im = Image.frombytes("RGB", (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3])
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 58, 17), fill=(0, 0, 0))
    d.text((3, 0), "%.1f" % (a + i * step), font=font, fill=(255, 230, 60))
    sheet.paste(im, ((i % cols) * (W + 4), (i // cols) * (H + 4)))
sheet.save(out)
print(out, n)
