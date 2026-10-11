# -*- coding: utf-8 -*-
"""「OpenAI相关」封面验收（openai-cover 技能的硬性要求）：

  python check_cover.py <封面_B_16x9.png> [<封面_B_4x3.png> …]      同目录要有同名 .meta.json（make_cover.py 写的，里面有标题字框）

查：①尺寸 1920×1080 / 1440×1080；②左边 14 px 竖线是 OpenAI 蓝 #0285FF；③底色是 #050505（左上角）；④标题字框里有白字和 OpenAI 蓝字；
⑤字框在 B 站 16:10 安全区内（16:9：x 96–1824；4:3：x 60–1380）；⑥（只警告）16:9 的 x > 1824 一带还有明显的亮内容 = 主体会被首页卡片的 16:10 裁掉一块。
退出码 0 = 全部通过（警告不算失败）。出图后还是要打开 PNG 看一眼（字有没有压在主体的大字上、主体有没有被裁、有没有第三方水印）。
"""
import json
import sys
from pathlib import Path

from PIL import Image

BLUE, BG = (2, 133, 255), (5, 5, 5)


def near(c, ref, tol):
    return all(abs(a - b) <= tol for a, b in zip(c[:3], ref))


def check(png):
    png = Path(png)
    im = Image.open(png).convert("RGB")
    w, h = im.size
    probs, warns = [], []
    wide = (w, h) == (1920, 1080)
    if not wide and (w, h) != (1440, 1080):
        probs.append(f"尺寸 {w}×{h}，应该是 1920×1080 或 1440×1080")
    bar = [im.getpixel((7, y)) for y in (60, h // 2, h - 60)]
    if not all(near(p, BLUE, 14) for p in bar):
        probs.append(f"左边竖线颜色 {bar} 不是 OpenAI 蓝 #0285FF")
    if not near(im.getpixel((34, 24)), BG, 16):
        probs.append(f"左上角底色 {im.getpixel((34, 24))} 不是 #050505")
    meta_p = png.with_suffix(".meta.json")
    if meta_p.exists():
        t = json.loads(meta_p.read_text(encoding="utf-8"))["title"]
        x0, x1, y0, y1 = max(0, t["left"]), min(w, t["right"]), max(0, t["top"]), min(h, t["bottom"])
        px = list(im.crop((x0, y0, x1, y1)).getdata())
        n = len(px) or 1
        blue = sum(1 for p in px if near(p, BLUE, 45)) / n
        white = sum(1 for p in px if min(p) >= 235) / n
        if blue < 0.012:
            probs.append(f"标题字框里 OpenAI 蓝只占 {blue:.1%}（第 2 行要用 #0285FF）")
        if white < 0.03:
            probs.append(f"标题字框里白字只占 {white:.1%}（第 1 行要白）")
        lo, hi = (96, 1824) if wide else (60, 1380)
        if t["left"] < lo or t["right"] > hi:
            probs.append(f"字框 x {t['left']}–{t['right']} 超出安全区 {lo}–{hi}")
    else:
        warns.append("没有 .meta.json，跳过标题字框检查")
    if wide:
        strip = im.crop((1824, 90, 1920, 990))
        lum = sum(sum(p) / 3 for p in strip.getdata()) / (strip.width * strip.height)
        if lum > 45:
            warns.append(f"x > 1824 一带还有亮内容（平均亮度 {lum:.0f}）：B 站首页卡片裁成 16:10 时这块会被切掉，确认切掉不影响主体")
    print(f"{png.name}: {'通过' if not probs else '不合格：' + '；'.join(probs)}" + (f"；警告：{'；'.join(warns)}" if warns else ""))
    return not probs


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if args else 1)
    ok = all([check(p) for p in args])
    sys.exit(0 if ok else 1)
