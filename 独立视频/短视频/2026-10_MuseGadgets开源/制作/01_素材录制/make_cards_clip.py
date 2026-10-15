# -*- coding: utf-8 -*-
"""官网「Project Ideas」轮播（8 张卡片，cap_cards.py 截的 2× 像素真实页面）→ 1474×829 横向滚动片段 cards_carousel.mp4。
滚动和高亮框按 carousel_schedule.json 排（时间是片段内的秒数 = 场景开头起的秒数）：
  {"dur": 11.0, "scroll": [[0, 0], [7.4, 0], [8.2, 1040], [11, 1040]],          # [时刻, 横向偏移（卡片像素，2×）]，相邻关键帧之间缓动
   "hl": [[2.6, 4.2, 0], [4.4, 5.9, 1], ...]}                                      # [起, 止, 第几张卡片]：橙色框住这张卡片
没有 schedule 文件就用默认的（按估时排的）。配音出来后用真实时间重排、重渲（约 20 秒）。"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

BASE = Path(r"D:\大疆\独立视频\素材\2026-10_MuseGadgets开源\官网与仓库")
CARDS = BASE / "cards"
OUT = BASE / "cards_carousel.mp4"
SCHED = Path(__file__).with_name("carousel_schedule.json")
FW, FH, FPS = 1474, 830, 30       # 829 是奇数，libx264 yuv420p 要偶数高；引擎抽帧时会缩到 1474×829（比例差 0.1%）
CW, CH = 520, 768                      # 卡片在 2× 下的像素
PAD = (FH - CH) // 2                   # 上下留白（白底）
ORANGE = (255, 79, 26)

DEFAULT = {"dur": 11.0,
           "scroll": [[0, 0], [7.4, 0], [8.3, 1040], [11.0, 1040]],
           "hl": [[2.6, 4.2, 0], [4.4, 5.9, 1], [6.1, 7.4, 2], [8.6, 10.4, 3]]}


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def scroll_at(keys, t):
    if t <= keys[0][0]:
        return float(keys[0][1])
    for (t0, x0), (t1, x1) in zip(keys, keys[1:]):
        if t <= t1:
            return x0 + (x1 - x0) * ease((t - t0) / (t1 - t0)) if t1 > t0 else float(x1)
    return float(keys[-1][1])


def build_strip():
    n = len([f for f in CARDS.glob("card_*.png")])
    strip = Image.new("RGB", (CW * n, FH), (255, 255, 255))
    for i in range(n):
        strip.paste(Image.open(CARDS / f"card_{i}.png").convert("RGB"), (i * CW, PAD))
    d = ImageDraw.Draw(strip)                              # 卡片上下缘补一条细线，像轮播行的边
    for y in (PAD, PAD + CH - 1):
        d.line([(0, y), (CW * n, y)], fill=(208, 206, 202), width=2)
    return strip, n


def main():
    sch = json.loads(SCHED.read_text(encoding="utf-8")) if SCHED.exists() else DEFAULT
    strip, n = build_strip()
    max_x = CW * n - FW
    total = sch["dur"]
    frames = int(round(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{FW}x{FH}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(OUT)], stdin=subprocess.PIPE)
    for k in range(frames):
        t = k / FPS
        x = min(max(scroll_at(sch["scroll"], t), 0), max_x)
        im = strip.resize((FW, FH), Image.LANCZOS, box=(x, 0, x + FW, FH)) if abs(x - round(x)) > 1e-3 else strip.crop((int(round(x)), 0, int(round(x)) + FW, FH))
        for t0, t1, ci in sch["hl"]:
            a = min(1.0, max(0.0, (t - t0) / 0.25)) * min(1.0, max(0.0, (t1 - t) / 0.25))
            if a <= 0.01:
                continue
            ov = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            cx0 = ci * CW - x
            r = (cx0 + 6, PAD + 6, cx0 + CW - 6, PAD + CH - 6)
            d.rounded_rectangle(r, radius=14, outline=ORANGE + (int(255 * a),), width=9)
            d.rounded_rectangle((r[0] - 8, r[1] - 8, r[2] + 8, r[3] + 8), radius=20, outline=ORANGE + (int(70 * a),), width=8)
            im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        ff.stdin.write(np.asarray(im).tobytes())
    ff.stdin.close(); ff.wait()
    print("done", OUT, total, "s", frames, "frames")


if __name__ == "__main__":
    main()
