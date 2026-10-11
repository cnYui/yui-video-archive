# -*- coding: utf-8 -*-
"""量成片里真实烧进去的字幕：每条字幕取中点抽一帧，在字幕带（y BAND_TOP–BAND_TOP+112）里找墨色（中文）/ 灰色（英文）像素的左右边界和高度。

  python check_subs_render.py

判据：中文 / 英文的实际墨迹宽度 ≤ MAX_W（940）、左右各留 ≥ 70 px；中文一行的字高应约 48 px（CSS 52 px 的 em，CJK 字面约 0.92 em），不是 33 px（ASS Fontsize 52 只有标准的 68.6 %）。
和 make_subs.py 里按 PIL em 52 / 30 px 量的宽度对照：两者应基本一致（差几个 px 是描边 / 字距）。
"""
import io
import json
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFont

import config as C

TL = json.loads((C.BUILD / "timeline.json").read_text(encoding="utf-8"))
MP4 = C.EP / "成片_竖屏_中英字幕.mp4"


def frame_at(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(MP4), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    return np.asarray(Image.open(io.BytesIO(raw)).convert("RGB")).astype(int)


def main():
    fz = ImageFont.truetype(str(C.FONTS / "NSC800.ttf"), C.ZH_PX)
    fe = ImageFont.truetype(str(C.FONTS / "NSC600.ttf"), C.EN_PX)
    cues = sorted((c for p in TL["passages"] for c in p["cues"]), key=lambda c: c["a"])
    worst = (0, 0)
    rows, heights = [], []
    for c in cues:
        t = (c["a"] + c["b"]) / 2
        im = frame_at(t)
        zh_band = im[C.BAND_TOP: C.BAND_TOP + 66]
        en_band = im[C.BAND_TOP + 66: C.BAND_TOP + 112]
        r, g, b = zh_band[..., 0], zh_band[..., 1], zh_band[..., 2]
        zh_mask = (r < 70) & (g < 70) & (b < 70)                         # 墨色 #141413
        r2, g2, b2 = en_band[..., 0], en_band[..., 1], en_band[..., 2]
        en_mask = (abs(r2 - 0x4B) < 28) & (abs(g2 - 0x55) < 28) & (abs(b2 - 0x63) < 28)   # 灰 #4B5563
        out = []
        for mask in (zh_mask, en_mask):
            ys, xs = np.where(mask)
            out.append((xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) > 20 else None)
        zw, ew = fz.getlength(c["zh"]), fe.getlength(c["en"])
        zr, er = out
        rows.append((t, c["zh"], zw, zr, ew, er))
        if zr:
            heights.append(zr[3] - zr[2] + 1)
        for r_ in (zr, er):
            if r_:
                worst = (max(worst[0], r_[1] - r_[0] + 1), min(r_[0], C.W - 1 - r_[1]) if worst[1] == 0 else min(worst[1], r_[0], C.W - 1 - r_[1]))
    print(f"{len(cues)} 条字幕；中文行字面高度（墨迹）中位数 {int(np.median(heights))} px（CSS 52 px 的 em ≈ 48 px；ASS Fontsize 52 只有约 33 px）")
    for t, zh, zw, zr, ew, er in rows[:6] + rows[-3:]:
        zs = f"{zr[1] - zr[0] + 1} px（左 {zr[0]} 右 {C.W - 1 - zr[1]}）" if zr else "—"
        es = f"{er[1] - er[0] + 1} px" if er else "—"
        print(f"  {t:7.2f}s  {zh}  中文墨迹 {zs}（PIL em 52 量 {zw:.0f}）  英文墨迹 {es}（PIL 量 {ew:.0f}）")
    print(f"全部字幕里最宽的一行 {worst[0]} px；离左右边缘最近 {worst[1]} px（要 ≥ 70）")
    return 0 if worst[0] <= C.W - 140 and worst[1] >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())
