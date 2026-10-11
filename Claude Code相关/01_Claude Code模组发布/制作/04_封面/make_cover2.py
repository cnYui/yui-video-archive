# -*- coding: utf-8 -*-
"""封面 C（用户 2026-10-02：“封面太丑了…能不能使用最后底部的这个作为背景？封面中出现的内容和标题不要重复，封面出现：Claude mod(模组)发布这几个字，标题则用：现在你可以修改Claude Code成自己喜欢的样子”；
看了三张候选背景后：“用第三种，claude的形象大一点的”）。

  python make_cover2.py            → 封面_C_16x9.png / 封面_C_4x3.png，并复制成 封面_选定_16x9.png / 封面_选定_4x3.png
  python make_cover2.py variants   → 只出几张对比稿到 _src/variants/（不动正式文件）

背景：claude.dev 官方教程页最底部的太空场景（`footer .scene`），capture_scene.py 用深色模式、设备像素比 6 截的（`_src/scene/s6_*.png`，场景 1425×675 CSS 像素；
星空画布本身只有 2 倍，宇航员是 DOM 元素，6 倍下依然清晰）。这是官方页面的真实截图，不是重画。
“第三种”背景 = 候选 cand_c_tight：约 3 倍的紧裁，宇航员原本在画面 72% / 64% 处。做法：
  1. 把宇航员（身体橙色 + 头盔白线 + 黄色小星光）从截图里抠出来——抠成带透明度的小图；
  2. 星空背景 = 擦掉宇航员的截图，按“第三种”的位置和 3 倍裁出来，只把灰色星点提亮一点；
  3. 宇航员按 sprite 倍数放大（原图 3 倍 → 5 倍多），贴回去；再叠上字。
封面上只有一行字“Claude mod(模组)发布”（和标题不重复），没有别的字。
"""
import base64
import io
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SCENE = HERE / "_src" / "scene" / "s6_0.png"     # 8550×4056（设备像素比 6）；第 0 帧带黄色小星光
VAR = HERE / "_src" / "variants"
DSF = 6
BG_LIFT = 1.7          # 灰色星点亮度 = 20 + (原亮度 − 20) × BG_LIFT（背景底色 #141413，约 20）
ORANGE = "#D97757"     # 宇航员身体的颜色（取样得 217,119,87），也是 Claude 的品牌橙
IVORY = "#FAF9F5"


def uri(im, q=95):
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# ---- 把宇航员抠出来，并得到“没有宇航员的星空” ----
_src = Image.open(SCENE).convert("RGB")
_a = np.asarray(_src)                                                                    # uint8，别转 int（8550×4056 转 int64 要 800 MB）
_body = (_a[..., 0] > 170) & (_a[..., 1] > 80) & (_a[..., 1] < 150) & (_a[..., 2] < 120)  # 宇航员的橙色身体
_ys, _xs = np.where(_body)
CX, CY = int(_xs.mean()), int(_ys.mean())                                               # 宇航员重心（6 倍图里的像素）
BGCOL = tuple(int(v) for v in _a[8, 8])                                                  # 场景底色（应为 20,20,19）
WX0, WX1, WY0, WY1 = CX - 340, CX + 340, CY - 330, CY + 260                              # 宇航员 + 头盔 + 小星光所在的窗口
_win = _src.crop((WX0, WY0, WX1, WY1))
_w = np.asarray(_win).astype(np.int16)
_core = ((_w.max(axis=2) - _w.min(axis=2)) > 30) | (_w.max(axis=2) > 175)                # 橙 / 黄 / 白：宇航员的像素（灰色星点亮度 ≤ 140，不会被选中）
_mask = Image.fromarray((_core * 255).astype(np.uint8), "L").filter(ImageFilter.MaxFilter(21))   # 向外胀 10 px，把边缘和一圈暗边包进来
_fill = _mask.copy()
ImageDraw.floodfill(_fill, (0, 0), 128)                                                  # 从窗口角上灌水，灌不到的（眼睛）就是洞
_alpha = np.asarray(_mask).copy()
_alpha[np.asarray(_fill) == 0] = 255                                                     # 眼睛的洞补上（里面是底色，贴回去还是黑眼睛）
ALPHA = Image.fromarray(_alpha, "L")
_sp = np.where(_core[..., None], _w, np.array(BGCOL)).astype(np.uint8)                   # 抠出来的宇航员：非宇航员的像素一律换成底色（没有灰星点）
SPRITE = Image.fromarray(np.dstack([_sp, _alpha]), "RGBA")                               # 窗口大小的透明图，锚点（重心）在 (CX-WX0, CY-WY0)
ANCHOR = (CX - WX0, CY - WY0)
_clean = _src.copy()
_clean.paste(Image.new("RGB", _win.size, BGCOL), (WX0, WY0), ALPHA)                      # 擦掉宇航员的星空


def starfield(w, h, scale, bx, by):
    """scale = 封面像素 / 场景 CSS 像素；原来宇航员所在的位置落在封面 (bx*w, by*h)；只提亮灰色星点。"""
    rw, rh = w / scale * DSF, h / scale * DSF
    x0 = min(max(CX - bx * rw, 0), _clean.width - rw)
    y0 = min(max(CY - by * rh, 0), _clean.height - rh)
    im = _clean.crop((round(x0), round(y0), round(x0 + rw), round(y0 + rh))).resize((w, h), Image.LANCZOS)
    b = np.asarray(im).astype(float)
    lifted = np.clip(20 + (b - 20) * BG_LIFT, 0, 255)
    sat = b.max(axis=2) - b.min(axis=2)
    wgt = np.clip((sat - 10) / 30, 0, 1)[..., None]
    return Image.fromarray((lifted * (1 - wgt) + b * wgt).astype(np.uint8))


def compose(ly):
    """星空 + 放大的宇航员（重心落在 (ax*w, ay*h)，sprite = 封面像素 / 场景 CSS 像素）。"""
    w, h = ly["w"], ly["h"]
    im = starfield(w, h, ly["bg"], ly["bx"], ly["by"]).convert("RGBA")
    k = ly["sprite"] / DSF
    sp = SPRITE.resize((round(SPRITE.width * k), round(SPRITE.height * k)), Image.LANCZOS)
    im.alpha_composite(sp, (round(ly["ax"] * w - ANCHOR[0] * k), round(ly["ay"] * h - ANCHOR[1] * k)))
    return im.convert("RGB")


CSS = """
<link rel="stylesheet" href="file:///D:/大疆/AI科普/素材/字体/fonts.css">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:__W__px; height:__H__px; overflow:hidden; background:#141413; font-family:'Noto Sans SC', sans-serif; }
.bg { position:absolute; inset:0; background:url(__BG__) center/100% 100% no-repeat; }
.t { position:absolute; left:__X__px; font:900 __FS__px/1 'Noto Sans SC'; letter-spacing:-.01em; white-space:nowrap; text-shadow:0 8px 40px rgba(0,0,0,.7);
     -webkit-text-stroke:16px #141413; paint-order:stroke fill; }      /* 描一圈和底色一样的暗边（在字下面），挤掉紧贴字边的星点，字更干净 */
.t1 { top:__Y1__px; color:__C1__; }
.t2 { top:__Y2__px; color:__C2__; }
</style>
"""

# w, h；bg = 星空的放大倍数（封面像素/场景 CSS 像素），bx/by = 原宇航员位置在封面上的比例（“第三种”：3 倍、72%/64%）；
# sprite = 宇航员的放大倍数（身体宽约 64 CSS 像素；原图 3 倍），ax/ay = 宇航员重心在封面上的位置比例；x/y1/y2/fs = 字的位置和字号（y2 = y1 + 1.08×fs）
# B站首页卡片会把 16:9 裁成 16:10（左右各切约 96 px）：字和宇航员都收在 96–1824 之间
LAYOUT = {
    "16x9": dict(w=1920, h=1080, bg=3.0, bx=0.72, by=0.64, sprite=6.4, ax=0.75, ay=0.69, x=128, y1=150, y2=382, fs=215),
    "4x3": dict(w=1440, h=1080, bg=3.0, bx=0.72, by=0.64, sprite=5.0, ax=0.70, ay=0.76, x=84, y1=100, y2=316, fs=200),
}


def page(ly):
    rep = dict(W=ly["w"], H=ly["h"], BG=uri(compose(ly)), X=ly["x"], Y1=ly["y1"], Y2=ly["y2"], FS=ly["fs"], C1=IVORY, C2=ORANGE)
    s = CSS
    for k, v in rep.items():
        s = s.replace(f"__{k}__", str(v))
    return s + '<div class="bg"></div><div class="t t1">Claude mod</div><div class="t t2">(模组)发布</div>'


def render(pw_browser, ly, out):
    pg = pw_browser.new_page(viewport={"width": ly["w"], "height": ly["h"]})
    pg.set_content("<!doctype html><html><head><meta charset='utf-8'></head><body>" + page(ly) + "</body></html>")
    pg.evaluate("document.fonts.ready.then(() => true)")
    pg.wait_for_timeout(900)
    pg.screenshot(path=str(out))
    pg.close()
    print("->", out)


VARIANTS = {
    "n1": dict(),
    "n2": dict(sprite=6.2, ax=0.76, ay=0.68, fs=205, y1=150, y2=311),
    "n3": dict(sprite=5.0, ax=0.74, ay=0.70, fs=232, y1=130, y2=381),
    "n4": dict(bg=2.4, sprite=5.6, bx=0.70, by=0.62),               # 星空更大一块（更多星点）
}


def main():
    variants = len(sys.argv) > 1 and sys.argv[1] == "variants"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        if variants:
            VAR.mkdir(parents=True, exist_ok=True)
            for k, patch in VARIANTS.items():
                ly = {**LAYOUT["16x9"], **patch}
                ly["y2"] = patch.get("y2", round(ly["y1"] + 1.08 * ly["fs"]))
                render(b, ly, VAR / f"v_{k}.png")
        else:
            for name, ly in LAYOUT.items():
                render(b, ly, HERE / f"封面_C_{name}.png")
        b.close()
    if not variants:
        for name in LAYOUT:
            shutil.copy2(HERE / f"封面_C_{name}.png", HERE / f"封面_选定_{name}.png")
        print("封面_选定_* = C")


if __name__ == "__main__":
    main()
