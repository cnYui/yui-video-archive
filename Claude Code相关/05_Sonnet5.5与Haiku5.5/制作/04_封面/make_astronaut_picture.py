# -*- coding: utf-8 -*-
"""封面候选 C 的底图：Claude 官方像素宇航员（claude-code-cover 的 mascot.py：官方 40×33 像素表 + 动作 bolt = 提速 / 新模型）放在深色底上，
1150×1000，和 make_mascot_pictures.py 出的八爪鱼底图同尺寸，交给 make_cover_framed.py 加边框和大字。形象只来自 mascot.py，不重新上色。
  python make_astronaut_picture.py
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

SK = Path(r"D:\大疆\Claude Code相关\skill\claude-code-cover\scripts")
sys.path.insert(0, str(SK))
import mascot  # noqa: E402

HERE = Path(__file__).resolve().parent
W, H = 1150, 1000
SCHEME, POSE, CELL = "night", "bolt", 22


def main():
    sc = mascot.SCHEMES[SCHEME]
    sp = mascot.render(mascot.build(POSE), CELL, SCHEME)
    bg = mascot.hex2rgb(sc["bg"])
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    rnd = random.Random(7)                                   # 像素小星点（品牌深灰 / 淡黄），避开宇航员的外框
    sx0, sy0, sx1, sy1 = sp.bbox
    ox, oy = (W - sp.im.width) // 2, (H - sp.im.height) // 2 + 30
    box = (ox + sx0 - 40, oy + sy0 - 40, ox + sx1 + 40, oy + sy1 + 40)
    for _ in range(46):
        x, y, s = rnd.randrange(30, W - 30), rnd.randrange(30, H - 30), rnd.choice((6, 6, 10))
        if box[0] < x < box[2] and box[1] < y < box[3]:
            continue
        d.rectangle([x, y, x + s - 1, y + s - 1], fill=mascot.hex2rgb(rnd.choice(sc["deco"])))
    im.paste(sp.im, (ox, oy), sp.im)
    out = HERE / "_src"
    out.mkdir(exist_ok=True)
    im.save(out / "AST_C.png")
    print("AST_C.png", im.size, "宇航员图", sp.im.size, "cell", CELL)


if __name__ == "__main__":
    main()
