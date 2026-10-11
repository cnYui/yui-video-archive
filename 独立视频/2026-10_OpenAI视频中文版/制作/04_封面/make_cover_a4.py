# -*- coding: utf-8 -*-
"""封面 A4：A3（白字蓝外勾线 + 黑块“dots”）加上 OpenAI 官方 dots 的四只小角色（官方图抠出来的，cutout_dots.py）。

  python cutout_dots.py      # 先抠图（只需一次）
  python make_cover_a4.py    # 出 封面_A4_16x9.png / 封面_A4_4x3.png

版面：角色从封面底边探出头来（官方图里它们本来就是被画面底边切平的），所以底边正好藏住切口。
  16:9  一行标题（上移一点）+ 角色居中放在下面。
  4:3   两行标题左对齐：“OpenAI 重新演示”在上；黑块“dots”在下，角色紧挨着它站在右边。
底部那条白底小字（DevDay 2026｜订机票 · 选酒店 · 整理用户反馈｜中文同传）和视频标题重复，给角色腾位置，这一版去掉；要保留看 A3。
"""
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

from make_cover3 import HERE, fit, font, load, tw
from make_cover_final import black_shade, blue_outlined_text, pill_word

CUT = HERE.parents[1] / "素材" / "dots形象" / "官方" / "dots_四只_抠图.png"


def dots_group(width):
    cut = Image.open(CUT)
    return cut.resize((int(width), int(round(cut.height * width / cut.width))), Image.LANCZOS)


def put(img, layer, x, y):
    """把带透明的小图贴到 (x, y)；超出画布的部分直接裁掉。"""
    top = Image.new("RGBA", img.size, (0, 0, 0, 0))
    top.paste(layer, (int(x), int(y)))
    img.alpha_composite(top)


def clean_laptop_sticker(img):
    """原片 4.6 s 这帧里，笔记本盖上有个很糊的小贴纸（像一只灰色的 dots），标题上移后会从“dots”黑块下面露出来，
    和旁边的官方角色放一起很乱：用周围的笔记本盖颜色补掉（只在封面用，不动原片）。"""
    a = np.array(img.convert("RGB"))
    mask = np.zeros(a.shape[:2], np.uint8)
    cv2.ellipse(mask, (1480, 757), (76, 60), 0, 0, 360, 255, -1)          # 贴纸本体
    cv2.ellipse(mask, (1493, 702), (22, 24), 0, 0, 360, 255, -1)          # 贴纸头上那一小块青蓝色
    return Image.fromarray(cv2.inpaint(a, mask, 9, cv2.INPAINT_TELEA))


def shift_up(img, dy):
    """整张照片上移 dy 像素，底部用最后几行拉伸补上（反正那里会被压暗）。"""
    if not dy:
        return img
    W, H = img.size
    out = Image.new("RGBA", (W, H))
    out.paste(img.crop((0, dy, W, H)), (0, 0))
    strip = img.crop((0, H - 6, W, H)).resize((W, dy), Image.BILINEAR)
    out.paste(strip, (0, H - dy))
    return out


def make(W, H, gw, dy=0, left=False):
    wide = W / H > 1.5
    img = fit(clean_laptop_sticker(load("g_4.6.png")), W, H, cx=0.5 if wide else 0.0, cy=0.3).convert("RGBA")
    img = shift_up(img, dy)
    img = black_shade(img, H * (0.44 if wide else 0.40))
    grp = dots_group(gw)
    if wide:                                       # 一行标题 + 角色居中探出底边
        size, stroke = 150, 15
        f = font(size, 900)
        left = "OpenAI 重新演示"
        d = ImageDraw.Draw(img)
        wl, wd = tw(d, left, f), tw(d, "dots", f) + 2 * size * 0.30
        gap = size * 0.26
        x = (W - (wl + gap + wd)) / 2
        base = H * 0.652
        blue_outlined_text(img, (x, base), left, f, "ls", stroke)
        pill_word(img, x + wl + gap, base, size, "dots")
        put(img, grp, (W - grp.width) / 2, H - grp.height + 8)
    else:                                          # 两行：上面“OpenAI 重新演示”，下面黑块“dots” + 角色
        size, stroke = 138, 13
        f = font(size, 900)
        base1 = H * 0.640
        if left:                                   # 和黑块“dots”左对齐
            blue_outlined_text(img, (70 + stroke, base1), "OpenAI 重新演示", f, "ls", stroke)
        else:
            blue_outlined_text(img, (W / 2, base1), "OpenAI 重新演示", f, "ms", stroke)
        size2 = 150
        x0 = 70
        right = pill_word(img, x0, base1 + size2 * 1.18, size2, "dots")
        put(img, grp, W - 40 - grp.width, H - grp.height + 6)
    return img.convert("RGB")


def main():
    which = sys.argv[1:] or ["16x9", "4x3"]
    cfg = {"16x9": (1920, 1080, 1080, 0, False), "4x3": (1440, 1080, 860, 0, True)}
    for tag in which:
        w, h, gw, dy, left = cfg[tag]
        out = HERE / f"封面_A4_{tag}.png"
        make(w, h, gw, dy, left).save(out)
        print(out.name)


if __name__ == "__main__":
    main()
