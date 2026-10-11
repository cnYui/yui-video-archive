# -*- coding: utf-8 -*-
"""封面 A5：A4（官方 dots 四只角色 + 白字蓝外勾线 + 黑块）改文字。用户原话：“把这里你设定的图片内容修改为‘公开演示翻车后，重新演示倒车’，
然后把底部的‘订机票、选酒店’去掉”。

  python make_cover_a5.py          # 出 封面_A5_dots_*（16:9 / 4:3）

“倒车”我怀疑是语音输入把 dots 听成了倒车（整个视频讲的是 dots），所以两种写法都出：dots = 黑块里写 dots；倒车 = 照字面写“倒车”。
用户后来说“我说错了”，要的是 dots，定了 dots 版（之后又缩减成 A6，见 make_cover_a6.py）；倒车版作废，只在命令行写 倒车 时才出：python make_cover_a5.py 倒车
版面：两行居中——“公开演示翻车后”/“重新演示 + 黑块”（逗号在换行处省掉），下面是角色从底边探出头；照片整体上移，给两行字腾地方。
底部小字（订机票 · 选酒店 · 整理用户反馈 · 中文同传）整条没有了，标题里已经有。
"""
import sys

from PIL import ImageDraw

from make_cover3 import HERE, fit, font, load, tw
from make_cover_a4 import clean_laptop_sticker, dots_group, put, shift_up
from make_cover_final import black_shade, blue_outlined_text, pill_word

LINE1 = "公开演示翻车后"
LINE2 = "重新演示"


def make(W, H, last, size=136, dy=80, gw=1000, b1=564):
    wide = W / H > 1.5
    stroke = round(size * 0.10)
    img = fit(clean_laptop_sticker(load("g_4.6.png")), W, H, cx=0.5 if wide else 0.0, cy=0.3).convert("RGBA")
    img = shift_up(img, dy)
    img = black_shade(img, H * 0.42)
    f = font(size, 900)
    d = ImageDraw.Draw(img)
    b2 = b1 + 1.18 * size
    blue_outlined_text(img, (W / 2, b1), LINE1, f, "ms", stroke)
    wl, wp = tw(d, LINE2, f), tw(d, last, f) + 2 * size * 0.30
    gap = size * 0.26
    x = (W - (wl + gap + wp)) / 2
    blue_outlined_text(img, (x, b2), LINE2, f, "ls", stroke)
    pill_word(img, x + wl + gap, b2, size, last)
    grp = dots_group(gw)
    put(img, grp, (W - grp.width) / 2, H - grp.height + 8)
    return img.convert("RGB")


def main():
    for name in sys.argv[1:] or ["dots"]:
        last = name
        for tag, (w, h) in (("16x9", (1920, 1080)), ("4x3", (1440, 1080))):
            out = HERE / f"封面_A5_{name}_{tag}.png"
            make(w, h, last).save(out)
            print(out.name)


if __name__ == "__main__":
    main()
