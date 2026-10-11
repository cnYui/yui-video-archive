# -*- coding: utf-8 -*-
r"""草稿用的“占位人像”：悠一还没出镜时，用一张静态图（头像剪影 + “悠一 出镜位”）当小窗里的画面，
让 compose_face_mixed.py 能按真实位置 / 缓动 / 字幕检查把小窗叠出来，预览版式。输出 _face_placeholder.mp4（1920×1080，30 fps，静止）。
悠一的真视频来了：改 face.json 的 src / start / crop，把 mirror 改回 true，这个文件就不用了。"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"
W, H = 1920, 1080
im = Image.new("RGB", (W, H), "#EDE6D6")
d = ImageDraw.Draw(im)
for k in range(-H, W, 56):                                   # 斜纹，和画面里别的占位同一种语言
    d.line([(k, 0), (k + H, H)], fill="#E3DAC7", width=18)
cx, cy = W // 2, H // 2
d.ellipse([cx - 175, cy - 330, cx + 175, cy + 20], fill="#B9AE97")        # 头
d.pieslice([cx - 400, cy + 60, cx + 400, cy + 760], 180, 360, fill="#B9AE97")  # 肩
f = ImageFont.truetype(FONT, 104)
f.set_variation_by_axes([900])
t = "悠一 出镜位"
tw = d.textlength(t, font=f)
d.text((cx - tw / 2, cy + 120), t, font=f, fill="#1F1B16")
f2 = ImageFont.truetype(FONT, 52)
f2.set_variation_by_axes([700])
t2 = "占位 · 镜像人像会放这里"
d.text((cx - d.textlength(t2, font=f2) / 2, cy + 260), t2, font=f2, fill="#6B6458")
png = HERE / "_face_placeholder.png"
im.save(png)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", str(png), "-t", "300", "-c:v", "libx264", "-tune", "stillimage",
                "-crf", "20", "-pix_fmt", "yuv420p", str(HERE / "_face_placeholder.mp4")], check=True)
print("ok")
