# -*- coding: utf-8 -*-
"""封面素材：人像抠图（birefnet，本地 ~/.u2net，不联网）+ 白描边；小程序截图裁成手机屏、抹掉鼠标箭头。

  python cutout.py            → face_cut/<名字>.png、<名字>_outline.png；app_cut/app_home.png

人像帧：2026-10-01 SD 卡已拔，先用 720p 出镜代理（02_出镜/proxy）的帧做方案；用户选定后插回 SD 卡，
用 4K 原片同一时刻重抽一帧（ffmpeg -ss <秒> -i <原片> -frames:v 1 -q:v 2）换掉 face_src 里的图再跑一次。
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from rembg import new_session, remove

HERE = Path(__file__).resolve().parent
# 第一版用了举手挥手的帧（hello / bye / talk），用户 2026-10-01：“举手这个有点丑……换一个正常的图片就行”。
PICK = {"smile": "p0161_193.2", "calm": "p0162_186.4", "smile2": "p0161_192.9"}   # 说完拜拜后的微笑 / 开场口播结尾平静正对镜头 / 微笑、嘴唇微开
OUTLINE = 9                           # 白边宽（720p 原图像素；放大到封面约 12 px）


def person(sess, name, src):
    im = Image.open(HERE / "face_src" / f"{src}.png").convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    cut = remove(im, session=sess)
    a = np.array(cut.split()[-1])
    # 留最大的一块，和面积不小的几块（举起来的手可能和身体不连着）；背景里的小杂块去掉
    n, lab_, stats, _ = cv2.connectedComponentsWithStats((a > 32).astype(np.uint8), 8)
    if n > 2:
        areas = stats[1:, cv2.CC_STAT_AREA]
        keep = [1 + k for k, s in enumerate(areas) if s >= 0.05 * areas.max()]
        a = np.where(np.isin(lab_, keep), a, 0).astype(np.uint8)
        cut.putalpha(Image.fromarray(a))
    ys, xs = np.nonzero(a > 16)
    box = (max(0, xs.min() - 30), max(0, ys.min() - 30), min(a.shape[1], xs.max() + 30), a.shape[0])
    cut = cut.crop(box)
    # 720p 源放大到封面会软：先 2 倍 Lanczos，再轻微锐化
    cut = cut.resize((cut.width * 2, cut.height * 2), Image.LANCZOS)
    rgb = cut.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
    cut = Image.merge("RGBA", (*rgb.split(), cut.split()[-1]))
    (HERE / "face_cut").mkdir(exist_ok=True)
    cut.save(HERE / "face_cut" / f"{name}.png")
    al = cut.split()[-1].filter(ImageFilter.MaxFilter(OUTLINE * 4 + 1)).filter(ImageFilter.GaussianBlur(1.5))
    white = Image.new("RGBA", cut.size, (255, 255, 255, 0))
    white.putalpha(al)
    Image.alpha_composite(white, cut).save(HERE / "face_cut" / f"{name}_outline.png")
    # 头部中心（占图宽的比例）：取图高 8%–30% 的各行，左右边缘中点的中位数；封面按它摆人，不让手机压到脸
    al = np.array(cut.split()[-1]) > 128
    hh = al.shape[0]
    mids, widths = [], []
    for y in range(int(hh * 0.08), int(hh * 0.30)):
        xs_ = np.nonzero(al[y])[0]
        if len(xs_) > 10:
            mids.append((xs_[0] + xs_[-1]) / 2)
            widths.append(xs_[-1] - xs_[0])
    META[name] = {"w": cut.width, "h": cut.height, "fx": round(float(np.median(mids)) / cut.width, 4), "fw": round(float(np.median(widths)) / cut.width, 4)}
    print(name, src, cut.size, META[name], flush=True)


def app_shot():
    """R1041 48 s：例一做出来的小程序首页。裁手机屏，抹掉箭头。"""
    a = cv2.imread(str(HERE / "app_src" / "R1041_48.png"))
    # 鼠标箭头（黑芯白边）：在箭头附近找“很黑或很白、和周围差很多”的像素，膨胀后补
    x0, y0, x1, y1 = 818, 584, 884, 676
    roi = a[y0:y1, x0:x1]
    g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(roi, 21)
    diff = np.abs(roi.astype(int) - blur.astype(int)).sum(2)
    m = ((g < 70) | (diff > 90)).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    mask = np.zeros(a.shape[:2], np.uint8)
    mask[y0:y1, x0:x1] = m
    a = cv2.inpaint(a, mask, 9, cv2.INPAINT_TELEA)
    scr = a[12:1012, 590:1060]
    (HERE / "app_cut").mkdir(exist_ok=True)
    cv2.imwrite(str(HERE / "app_cut" / "app_home.png"), scr)
    print("app_home", scr.shape)


META = {}


def main():
    import json
    app_shot()
    sess = new_session("birefnet-general")
    for name, src in PICK.items():
        person(sess, name, src)
    (HERE / "face_cut" / "meta.js").write_text("window.FACEMETA = " + json.dumps(META) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
