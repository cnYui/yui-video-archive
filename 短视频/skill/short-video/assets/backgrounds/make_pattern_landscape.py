# -*- coding: utf-8 -*-
"""横版背景印花（2026-10-05，用户：“长视频背景也加上和短视频 skill 中相同的背景图片，你设计三张横版的图片，然后同步到 skill 中，之后横板视频也要随机选一张图片”）。

和竖屏三张（pattern_color / pattern_ink / pattern_orange）同一套 AI 编程工具图标、同样的图标大小和疏密（76 px，间距 176 × 168，每行错半格、随机转 ±14°、大小 0.86–1.12 倍），
只是画布换成 2340×1080（横版引擎的画面）、种子不同：

  python make_pattern_landscape.py   →  landscape_color.png（原色，约 11%）/ landscape_ink.png（墨色单色，约 7.5%）/ landscape_orange.png（橙色单色，约 12%）

三张都是 2340×1080 的透明 PNG（透明度已经烤进去），叠在底色上用（竖屏是米白 #FAF9F5；横版引擎原来是白底，印花淡到不影响，底色照引擎原来的）。
文件名以 landscape_ 开头：横版随机池只认这个前缀（竖屏池认 pattern_ 前缀，两边互不串）。图标缓存在 _icons\（没有就用 make_pattern.rasterize() 现渲，需要 Playwright）。
"""
from pathlib import Path

import make_pattern as mp

OUT = Path(__file__).resolve().parent
mp.W, mp.H = 2340, 1080

VARIANTS = [
    ("color", 0.11, "landscape_color.png", 21),
    ("ink", 0.075, "landscape_ink.png", 23),
    ("orange", 0.12, "landscape_orange.png", 29),
]


def main():
    if not (mp.ICON_DIR / "claudecode.png").exists():
        mp.rasterize()
    for variant, opacity, name, seed in VARIANTS:
        im = mp.make(variant, opacity, 176, 168, 76, seed)
        assert im.size == (2340, 1080), im.size
        im.save(OUT / name)
        print(name, im.size)


if __name__ == "__main__":
    main()
