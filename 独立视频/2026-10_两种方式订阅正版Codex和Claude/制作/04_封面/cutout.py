# -*- coding: utf-8 -*-
"""封面用的人像：开场出镜（DJI 0163）的帧 → 稍微提饱和度 → birefnet 抠像 → 白描边版。做法照《AI时代计算机专业研究生如何用AI》第 1 期的 cutout.py。
输出 face_cut/<名字>.png（RGBA）和 <名字>_outline.png（外面一圈白边 + 透明底）。模型在 ~/.u2net，本地运行，不联网。

本期：SD 卡已拔，帧从代理（../02_出镜/proxy/0163.mp4，1280×720，HLG 直接转 8-bit）取：
  ffmpeg -ss <秒> -i ../02_出镜/proxy/0163.mp4 -frames:v 1 -q:v 1 face_src/p0163_<秒>.jpg
要更清楚就把 SD 卡插回去，从 4K 原片按同样的秒数取（CROP 乘 3）。
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import new_session, remove

HERE = Path(__file__).resolve().parent
# 用户 2026-10-01：“使用正常的我的照片，不要出现挥手等等大动作的”——第一版的挥手（0.35 / 0.55 s）、伸手关相机（88.4 s）不用；
# 改取说话停顿里闭着嘴、两手放下、正对镜头的帧
PICK = {"calm_a": "p0163_87.2", "calm_b": "p0163_45.6", "calm_c": "p0163_52.5"}   # 说完最后一句（带一点笑）/ 停顿 / 停顿
CROP = (140, 0, 1160, 720)             # 代理 1280×720 里人在这块里（第一版挥手的手也在）
UPSCALE = 2                            # 代理分辨率低：先放大两倍再抠，边缘更顺
OUTLINE = 16                           # 白边宽（放大后的像素）


def main():
    sess = new_session("birefnet-general")
    (HERE / "face_cut").mkdir(exist_ok=True)
    for name, src in PICK.items():
        im = Image.open(HERE / "face_src" / f"{src}.jpg").convert("RGB").crop(CROP)
        im = im.resize((im.width * UPSCALE, im.height * UPSCALE), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.4, 50, 2))
        im = ImageEnhance.Color(im).enhance(1.12)
        im = ImageEnhance.Contrast(im).enhance(1.04)
        cut = remove(im, session=sess)                   # RGBA
        a = np.array(cut.split()[-1])
        # 只留最大的一块（背景里的晾衣架、手办之类会被误抠成小块）
        n, lab_, stats, _ = cv2.connectedComponentsWithStats((a > 32).astype(np.uint8), 8)
        if n > 2:
            keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
            a = np.where(lab_ == keep, a, 0).astype(np.uint8)
            cut.putalpha(Image.fromarray(a))
        ys, xs = np.nonzero(a > 16)
        box = (max(0, xs.min() - 40), max(0, ys.min() - 40), min(a.shape[1], xs.max() + 40), a.shape[0])
        cut = cut.crop(box)
        cut.save(HERE / "face_cut" / f"{name}.png")
        al = cut.split()[-1].filter(ImageFilter.MaxFilter(OUTLINE * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
        white = Image.new("RGBA", cut.size, (255, 255, 255, 0))
        white.putalpha(al)
        Image.alpha_composite(white, cut).save(HERE / "face_cut" / f"{name}_outline.png")
        print(name, src, "→", cut.size, flush=True)


if __name__ == "__main__":
    main()
