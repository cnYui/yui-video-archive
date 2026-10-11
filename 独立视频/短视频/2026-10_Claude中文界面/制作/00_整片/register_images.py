# -*- coding: utf-8 -*-
"""把用户给的截图（语言选择框、两条推文）裁一块、登记成 pageShot 能用的“页面图”，不用重新上网截。
输出 media/pages/<名字>.png，并把 {src, w, h, url, bg, marks} 写进 pages.json / pages.js。

  python register_images.py            全部重登记
  python register_images.py P_picker   只登记指定的几张

marks 的坐标写**原图像素**（x, y, w, h），脚本按裁切框换算；键以 "#sel:" 开头 = 画橙色边框（整块），否则 = 荧光笔。
"""
import json
import sys
from pathlib import Path

from PIL import Image

from common import MAT

HERE = Path(__file__).resolve().parent
OUT = HERE / "media" / "pages"
IMG = MAT / "2026-10_Claude中文界面"

# 名字: dict(src=原图文件名, crop=(x0, y0, x1, y1) 原图像素, url=浏览器顶栏里显示的文字, marks={标记名: (x, y, w, h)})
SPECS = {
    # 用户自己的 Claude（中文界面）里的“选择您的语言”弹窗，1066×765
    "P_picker": dict(src="用户截图_语言选择框_中文界面.png", crop=None, bg="#1F1F1F", url="Claude · 账号菜单 → 语言 → 选择您的语言",
                     marks={"title": (36, 24, 200, 42),
                            "#sel:zh_s": (37, 266, 310, 78),
                            "#sel:zh_t": (371, 266, 310, 78),
                            "#sel:all": (37, 170, 990, 560),
                            "lang_top": (54, 190, 700, 50)}),
    # @ScarletKc（KC）的推文截图（用户贴的，约发布后 3 小时），720×684
    "T_kc": dict(src="推文截图_KC_ScarletKc.png", crop=None, url="x.com/ScarletKc（推文截图）",
                 marks={"head": (58, 10, 250, 30),
                        "hook1": (58, 86, 500, 32),
                        "hook2": (58, 136, 450, 32),
                        "#sel:pic": (58, 175, 640, 450),
                        "views": (492, 638, 70, 28)}),
    # @Chris62771610 的推文，只留前两行（后面的几句、引用的那条都不用），734×132
    "T_chris": dict(src="推文截图_Chris_转Kin.png", crop=(0, 0, 734, 132), url="x.com/Chris62771610（推文截图，节选）",
                    marks={"head": (66, 12, 260, 30),
                           "joke": (66, 90, 340, 32)}),
}


def main():
    only = sys.argv[1:] or list(SPECS)
    OUT.mkdir(parents=True, exist_ok=True)
    mf = HERE / "pages.json"
    meta = json.loads(mf.read_text(encoding="utf-8")) if mf.exists() else {}
    for k in only:
        s = SPECS[k]
        im = Image.open(IMG / s["src"]).convert("RGB")
        x0, y0, x1, y1 = s.get("crop") or (0, 0, im.width, im.height)
        cr = im.crop((x0, y0, x1, y1))
        f = OUT / f"{k}.png"
        cr.save(f)
        ms = {}
        for name, r in s.get("marks", {}).items():
            rects = r if isinstance(r[0], (list, tuple)) else [r]
            ms[name] = [[int(round(x - x0)), int(round(y - y0)), int(round(w)), int(round(h))] for x, y, w, h in rects]
        bg = s.get("bg") or "#%02X%02X%02X" % cr.getpixel((6, cr.height - 6))
        meta[k] = {"src": f"pages/{k}.png", "w": cr.width, "h": cr.height, "url": s["url"], "bg": bg, "marks": ms}
        print(f"{k}: {cr.width}×{cr.height}，标记 {len(ms)} 个，底色 {bg}")
    mf.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "pages.js").write_text("window.PG = " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


if __name__ == "__main__":
    main()
