# -*- coding: utf-8 -*-
"""把 pages.json 里每张页面图上的高亮矩形画出来（橙框），输出到 素材\\...\\页面\\_check\\<key>_marks.png，检查高亮位置对不对。
  python check_marks.py            全部
  python check_marks.py A_3 A_9    指定
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import series_data as D  # noqa: E402

M = D.MAT / "页面"
meta = json.loads((M / "pages.json").read_text(encoding="utf-8"))
out = M / "_check"
out.mkdir(exist_ok=True)
keys = sys.argv[1:] or list(meta)
for key in keys:
    m = meta[key]
    im = Image.open(M / f"{key}.png").convert("RGB")
    dr = ImageDraw.Draw(im, "RGBA")
    for needle, rects in m["marks"].items():
        for x, y, w, h in rects:
            dr.rectangle([x - 4, y - 3, x + w + 4, y + h + 3], fill=(255, 106, 43, 90), outline=(255, 79, 26, 255), width=4)
    im = im.resize((640, int(im.height * 640 / im.width)))
    im.save(out / f"{key}_marks.png")
    print(key, {n[:28]: len(r) for n, r in m["marks"].items()})
print("检查图在", out)
