# -*- coding: utf-8 -*-
"""封面用的人像：从 4K 原片（HLG 10-bit，按出镜画面同样直接转 8-bit）取的帧 → 稍微提饱和度 → birefnet 抠像 → 白描边版。
输出 face_cut/<名字>.png（RGBA）和 <名字>_outline.png（外面一圈白边 + 透明底）。模型在 ~/.u2net，本地运行，不联网。"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import new_session, remove

HERE = Path(__file__).resolve().parent
PICK = {"wave": "0172_59.20", "wow": "0170_6.60", "talk": "0162_45.65"}
CROP = {"wave": (400, 0, 3840, 2160)}   # 人在画面中间；挥手那张手伸到右边，裁宽一点
CROP_DEFAULT = (560, 0, 3280, 2160)
OUTLINE = 22                           # 白边宽（原图像素）


def main():
    sess = new_session("birefnet-general")
    (HERE / "face_cut").mkdir(exist_ok=True)
    for name, src in PICK.items():
        im = Image.open(HERE / "face_src" / f"{src}.png").convert("RGB").crop(CROP.get(name, CROP_DEFAULT))
        im = ImageEnhance.Color(im).enhance(1.12)
        im = ImageEnhance.Contrast(im).enhance(1.04)
        cut = remove(im, session=sess)                   # RGBA
        a = np.array(cut.split()[-1])
        # 只留最大的一块（背景里的晾衣架带子之类会被误抠成小块）
        n, lab_, stats, _ = cv2.connectedComponentsWithStats((a > 32).astype(np.uint8), 8)
        if n > 2:
            keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
            a = np.where(lab_ == keep, a, 0).astype(np.uint8)
            cut.putalpha(Image.fromarray(a))
        ys, xs = np.nonzero(a > 16)
        box = (max(0, xs.min() - 60), max(0, ys.min() - 60), min(a.shape[1], xs.max() + 60), a.shape[0])
        cut = cut.crop(box)
        cut.save(HERE / "face_cut" / f"{name}.png")
        # 白描边：alpha 往外扩 OUTLINE 像素
        al = cut.split()[-1].filter(ImageFilter.MaxFilter(OUTLINE * 2 + 1)).filter(ImageFilter.GaussianBlur(1.2))
        white = Image.new("RGBA", cut.size, (255, 255, 255, 0))
        white.putalpha(al)
        ol = Image.alpha_composite(white, cut)
        ol.save(HERE / "face_cut" / f"{name}_outline.png")
        print(name, src, "→", cut.size, flush=True)


if __name__ == "__main__":
    main()
