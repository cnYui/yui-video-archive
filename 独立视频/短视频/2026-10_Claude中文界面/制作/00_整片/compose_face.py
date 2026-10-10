# -*- coding: utf-8 -*-
"""把悠一出镜视频（镜像）作为圆角小窗叠到成片上：卡片版成片（整片_v1_cards无小窗.mp4，已带混好的音轨）+ 原片 4K（H 盘）→ 整片_v1.mp4。
小窗 360×360，居中放在字幕下面（x 360、y 1664），边框和成片一样：7 px 黑描边 + 橙色硬阴影（14 px 偏移）+ 右上角黄贴纸。
原片从 0.20 s 起（和配音 tts_narration.wav 的起点一致），镜像（hflip）。"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SRC = Path(r"H:\DCIM\DJI_001\DJI_20261006130553_0177_D.MP4")
T0, DUR = 0.20, 62.69
W0, H0, SIZE, RAD = 360, 1664, 360, 30
CROP = (1700, 1128, 120)            # 4K 原片里裁一块 1700×1700（脸 + 肩膀），左上角 x=1128, y=120
FONT = Path(r"D:\大疆\Claude Code相关\短视频\02_Anthropic设计师用Claude做设计\制作\00_整片\fonts\NotoSansSC.ttf")
BASE = HERE / "整片_v1_cards无小窗.mp4"
OUT = HERE / "整片_v1.mp4"
L = HERE / "_face"; L.mkdir(exist_ok=True)

def layers():
    S = 3
    shadow = Image.new("RGBA", (1080 * S, 2340 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(shadow)
    d.rounded_rectangle([(W0 + 14) * S, (H0 + 14) * S, (W0 + SIZE + 14) * S, (H0 + SIZE + 14) * S], radius=RAD * S, fill=(0xFF, 0x4F, 0x1A, 255))
    shadow.resize((1080, 2340), Image.LANCZOS).save(L / "shadow.png")
    ring = Image.new("RGBA", (1080 * S, 2340 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(ring)
    d.rounded_rectangle([(W0 - 7) * S, (H0 - 7) * S, (W0 + SIZE + 7) * S, (H0 + SIZE + 7) * S], radius=(RAD + 7) * S, outline=(0x14, 0x14, 0x13, 255), width=7 * S)
    ring = ring.resize((1080, 2340), Image.LANCZOS)
    # 黄贴纸（右上角，倾斜 3°）
    f = ImageFont.truetype(str(FONT), 34); f.set_variation_by_axes([800])
    tw = int(f.getlength("悠一 出镜")) + 36; st = Image.new("RGBA", (tw, 58), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([0, 0, tw - 1, 57], radius=10, fill=(0xFF, 0xD8, 0x4D, 255), outline=(0x14, 0x14, 0x13, 255), width=4)
    sd.text((18, 6), "悠一 出镜", font=f, fill=(0x14, 0x14, 0x13, 255))
    st = st.rotate(-3, expand=True, resample=Image.BICUBIC)
    ring.alpha_composite(st, (W0 + SIZE - tw + 22, H0 - 12))
    ring.save(L / "ring.png")
    m = Image.new("L", (SIZE * S, SIZE * S), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, SIZE * S - 1, SIZE * S - 1], radius=RAD * S, fill=255)
    m.resize((SIZE, SIZE), Image.LANCZOS).save(L / "mask.png")

def main():
    layers()
    cw, cx, cy = CROP
    fc = (f"[1:v]fps=30,crop={cw}:{cw}:{cx}:{cy},scale={SIZE}:{SIZE}:flags=lanczos,hflip,format=gray,format=yuva420p[face0];" if False else
          f"[1:v]fps=30,crop={cw}:{cw}:{cx}:{cy},scale={SIZE}:{SIZE}:flags=lanczos,hflip,format=yuv420p[fc];"
          f"[4:v]format=gray[mk];[fc][mk]alphamerge[face];"
          f"[0:v][2:v]overlay=0:0[b1];[b1][face]overlay={W0}:{H0}[b2];[b2][3:v]overlay=0:0,format=yuv420p[v]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(BASE), "-ss", f"{T0}", "-t", f"{DUR}", "-i", str(SRC),
           "-loop", "1", "-t", f"{DUR}", "-i", str(L / "shadow.png"), "-loop", "1", "-t", f"{DUR}", "-i", str(L / "ring.png"), "-loop", "1", "-t", f"{DUR}", "-i", str(L / "mask.png"),
           "-filter_complex", fc, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "-shortest", str(OUT)]
    subprocess.run(cmd, check=True)
    print("ok ->", OUT)

if __name__ == "__main__":
    main()
