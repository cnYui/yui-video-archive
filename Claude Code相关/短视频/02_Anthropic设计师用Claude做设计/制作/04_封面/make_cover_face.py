# -*- coding: utf-8 -*-
r"""备选封面（干净的单人画面 + 钩子大字）：抖音的封面检测会给“封面不佳：请勿使用截屏当封面”（疑似视频通话截屏样的小窗画面，Tavus 那条遇到过），
所以另做一版 Nate 的脸铺满整个封面、不带边框 / 贴纸 / 下框 UI，只有大字：

  python make_cover_face.py     → cover_3x4_face.png（1080×1440）、cover_4x3_face.png（1440×1080）

画面 = make_cover_short.py 里同一帧（原片 31.94 s，4K 裁切 3000×1688）再按封面比例裁；大字放在下面（白字 + 墨描边 + 硬投影，强调行橙色），钩子同主封面。
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_cover_short as M  # noqa: E402

FACE_CX = 0.54          # 脸中心在 3000×1688 裁切里的位置（占比）


def crop_to(img, ratio, cx):
    """从 16:9 的图里裁一块 ratio（宽/高）的区域，水平中心 cx（占比），竖直取满高。"""
    w, h = img.size
    cw = min(w, int(round(h * ratio)))
    x0 = int(round(w * cx - cw / 2))
    x0 = max(0, min(w - cw, x0))
    return img.crop((x0, 0, x0 + cw, h))


def make(kind, w, h, ratio, fs_max, text_bottom_margin):
    face = M.grab(*M.TOP_FRAME, "top")
    im = crop_to(face, ratio, FACE_CX).resize((w, h), Image.LANCZOS)
    s = M.SS
    cv = im.resize((w * s, h * s), Image.LANCZOS)
    # 底部压暗一点，让白字更稳（渐变，只在文字区）
    grad = Image.new("L", (w * s, h * s), 0)
    gd = ImageDraw.Draw(grad)
    y0 = int(h * 0.55) * s
    for y in range(y0, h * s):
        gd.line([(0, y), (w * s, y)], fill=int(110 * (y - y0) / (h * s - y0)))
    cv.paste(Image.new("RGB", cv.size, (20, 20, 19)), (0, 0), grad)
    fs = M.measure(M.HOOK, w - 140, fs_max)[0]
    bh = fs * 1.14 * len(M.HOOK)
    fs, bw, bh = M.hook_text(cv, M.HOOK, 70, h - text_bottom_margin - bh, w - 140, fs_max, align="center")
    out = cv.resize((w, h), Image.LANCZOS)
    out.save(HERE / f"cover_{kind}_face.png")
    print(f"cover_{kind}_face.png {w}×{h}：大字 {fs} px")


def main():
    make("3x4", 1080, 1440, 3 / 4, 168, 90)
    make("4x3", 1440, 1080, 4 / 3, 168, 60)


if __name__ == "__main__":
    main()
