# -*- coding: utf-8 -*-
"""《Claude Code相关》合集的封面：B 站两个比例（16:9 = 1920×1080、4:3 = 1440×1080）各一张。

  python make_cover.py --line1 "Claude mod" --line2 "(模组)发布" --out "<…>/制作/04_封面" [--name C] [--scheme night] [--pose float] [--select [--force]]

硬性要求（用户 2026-10-02）：封面必须有 Claude 的像素形象（官方像素宇航员，要大；动作可以自己画）和 Claude 的品牌色（橙 #D97757、米白 #FAF9F5、淡黄 #F5DB9A、深色 #141413），
背景也用品牌色。本脚本把这几条做成默认：宇航员用 mascot.py 按格子渲染（整数倍、不糊，16:9 每格 18 px，身体宽 432 px），字只用该背景方案的两个字色。

背景方案 --scheme：
  night   深色 #141413 + 官方教程页底部的星空（第 1 期用的；字：米白 + 品牌橙）
  ivory   米白 #FAF9F5 + 像素星点（字：深色 + 深橙；头盔环改深色）
  orange  品牌橙 #D97757 + 像素星点（字：米白 + 深色；宇航员加 1 格深色描边，不然和底色混在一起）
  yellow  淡黄 #F5DB9A + 像素星点（字：深色 + 深橙）
动作 --pose：官方帧 float / float2 / float3 / stand；自画 wave cheer gear terminal megaphone flag shield plug gift point think bolt（python mascot.py list 看各自适合的内容）。
  道具会把宇航员撑宽：靠右的道具超出安全区时整体往左挪；不想挪就 --flip（镜像，道具朝左，朝着字的方向）或缩小 --cell-16x9。

其他参数：
  --line1 / --line2   封面字，两行（line2 可空，单行时位置下移一点）；封面字和视频标题不要写同一句话，一般 ≤ 12 个字
  --out / --name      输出目录 / 方案名 → 封面_<name>_16x9.png、封面_<name>_4x3.png（另有同名 .meta.json，给 check_cover.py 用）
  --select [--force]  同时复制成 封面_选定_16x9.png / 封面_选定_4x3.png（公开仓库的白名单只收这两个名字）；已有选定图要加 --force 才覆盖
  --flip --eyes happy|wink   镜像 / 换表情
  --cell-16x9 18 --cell-4x3 14                  宇航员每格像素数的上限（16:9 不要小于 16，用户要的是“大一点”）
  --mpos-16x9 0.75,0.81 --mpos-4x3 0.70,0.88    宇航员外框中心的 x 比例、外框底边的 y 比例（所有动作站在同一条地平线上）
  --no-fit            不自动缩小宇航员（默认：道具撑宽后字号低于 fs_fit 就把宇航员每格缩小 1 px 再试，直到字号够或缩到保底）
  --min-cell-16x9 16 --min-cell-4x3 12          自动缩小的保底每格像素（默认身体宽 20%，不会再小：再小就 < 17% / 18%，验收不过）；字号还是不够就由你换动作 / --flip / 缩短字
  --bg scene|pixel    星空来源：scene = 官方场景截图（只有 night 能用，默认）；pixel = 程序画的像素星点（其他方案默认）；--seed 换一批星点
  --bg-scale 3.0 --bg-anchor 0.72,0.64 --bg-shift 0,0      scene 星空的放大倍数 / 位置 / 平移（“第三种”紧裁）

依赖：assets/（brand.json、sprite.json、scene_clean.png 由 build_assets.py 生成；sprite_official.dat 由 fetch_sprite.py 取）、Playwright、
共用字体 D:\\大疆\\AI科普\\素材\\字体\\fonts.css（Noto Sans SC 900）。
"""
import argparse
import base64
import html
import io
import json
import random
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mascot as M  # noqa: E402

ASSETS = HERE.parent / "assets"
FONTS_CSS = Path(r"D:\大疆\AI科普\素材\字体\fonts.css")
DSF = 6
BG_LIFT = 1.7           # scene 星空：灰色星点亮度 = 20 + (原亮度 − 20) × BG_LIFT；橙色 / 黄色不动（按饱和度加权）

# w, h；cell = 宇航员每格像素；mpos = (宇航员外框中心的 x 比例, 外框底边的 y 比例)——所有动作站在同一条“地平线”上；x = 字左边；right = 字能到的最右边；y1 = 第一行顶；
# fs_max = 最大字号；fs_fit = --fit 时字号低于它就把宇航员缩小一格再试；gap = 字和宇航员之间至少留多少；
# safe = 宇航员左右不能出的范围（B 站首页卡片会把 16:9 裁成 16:10，左右各切约 96 px）；top / bottom = 宇航员上下不能出的范围（底部约 12% 给时长角标）
# min_cell = 自动缩小宇航员时每格的保底：身体 24 格宽，验收要 ≥ 画面宽的 17%（16:9，每格 ≥ 14）/ 18%（4:3，每格 ≥ 11）；保底定在身体宽 20%（16:9 每格 16、4:3 每格 12）——第 3 期用户选的封面就是 16 px / 字号 170
LAYOUT = {
    "16x9": dict(w=1920, h=1080, cell=18, min_cell=16, mpos=(0.75, 0.81), x=128, right=1816, y1=150, fs_max=230, fs_fit=190, gap=90, safe=(96, 1824), top=40, bottom=950),
    "4x3": dict(w=1440, h=1080, cell=14, min_cell=12, mpos=(0.70, 0.88), x=84, right=1380, y1=100, fs_max=210, fs_fit=170, gap=70, safe=(40, 1400), top=40, bottom=1020),
}


def pair(s):
    a, b = s.split(",")
    return float(a), float(b)


def hex2rgb(h):
    return M.hex2rgb(h)


def uri_png(im):
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def box_hits(box, rects, gx, gy):
    """box 外扩（左右 gx、上下 gy）后是否碰到 rects 里的任何一个矩形。"""
    b0, b1, b2, b3 = box[0] - gx, box[1] - gy, box[2] + gx, box[3] + gy
    for r in rects:
        if not (r[2] <= b0 or b2 <= r[0] or r[3] <= b1 or b3 <= r[1]):
            return True
    return False


# ---- 宇航员：渲染 + 摆放 ----
def place_mascot(ly, a):
    cv = M.build(a.pose, a.flip, a.eyes)
    sp = M.render(cv, ly["cell"], a.scheme)
    ox = round(ly["mpos"][0] * ly["w"] - (sp.bbox[0] + sp.bbox[2]) / 2)      # 外框中心对准 x
    oy = round(ly["mpos"][1] * ly["h"] - sp.bbox[3])                          # 外框底边对准 y（所有动作站在同一条地平线上）
    x0, y0, x1, y1 = ox + sp.bbox[0], oy + sp.bbox[1], ox + sp.bbox[2], oy + sp.bbox[3]
    dx = dy = 0
    if x1 > ly["safe"][1]:
        dx = ly["safe"][1] - x1
    if x0 + dx < ly["safe"][0]:
        dx = ly["safe"][0] - x0
    if y1 > ly["bottom"]:
        dy = ly["bottom"] - y1
    if y0 + dy < ly["top"]:
        dy = ly["top"] - y0
    ox, oy = ox + dx, oy + dy
    c = ly["cell"]
    rects = [(ox + (x - sp.origin[0]) * c, oy + (y - sp.origin[1]) * c, ox + (x - sp.origin[0] + 1) * c, oy + (y - sp.origin[1] + 1) * c)
             for (x, y) in cv.cells(exclude=M.DECO_CHARS)]
    bbox = [ox + sp.bbox[0], oy + sp.bbox[1], ox + sp.bbox[2], oy + sp.bbox[3]]
    return sp, (ox, oy), bbox, rects, (dx, dy)


# ---- 背景 ----
def starfield(scene, anchor, w, h, scale, bx, by, shift):
    """scale = 封面像素 / 场景 CSS 像素；原来宇航员所在的位置落在封面 (bx*w, by*h)；只提亮灰色星点。"""
    rw, rh = w / scale * DSF, h / scale * DSF
    x0 = min(max(anchor[0] - bx * rw + shift[0] * DSF, 0), scene.width - rw)
    y0 = min(max(anchor[1] - by * rh + shift[1] * DSF, 0), scene.height - rh)
    im = scene.crop((round(x0), round(y0), round(x0 + rw), round(y0 + rh))).resize((w, h), Image.LANCZOS)
    b = np.asarray(im).astype(float)
    lifted = np.clip(20 + (b - 20) * BG_LIFT, 0, 255)
    sat = b.max(axis=2) - b.min(axis=2)
    wgt = np.clip((sat - 10) / 30, 0, 1)[..., None]
    return Image.fromarray((lifted * (1 - wgt) + b * wgt).astype(np.uint8))


def pixel_deco(im, ly, sc, seed, avoid):
    """像素星点：小方块 + 菱形小星光，颜色取该方案的 deco / deco_spark；避开宇航员。"""
    rnd = random.Random(seed)
    d = ImageDraw.Draw(im)
    w, h = im.size
    u = max(4, ly["cell"] // 2)
    cols, rows = w // u, h // u
    for _ in range(int(w * h / 38000)):
        x, y, s = rnd.randrange(cols) * u, rnd.randrange(rows) * u, rnd.choice([1, 1, 1, 2])
        if box_hits((x, y, x + u * s, y + u * s), avoid, 40, 40):
            continue
        d.rectangle([x, y, x + u * s - 1, y + u * s - 1], fill=hex2rgb(rnd.choice(sc["deco"])))
    for _ in range(8):
        for _try in range(60):
            px, py = rnd.randrange(2, cols - 3) * u, rnd.randrange(2, rows - 3) * u
            if px < ly["safe"][0] + 10 or px + 3 * u > ly["safe"][1] - 10:
                continue                      # 小星光（橙 / 淡黄）别落在 16:10 会被裁掉的两侧：验收会把两侧的橙色数成“字溢出”
            if box_hits((px, py, px + 3 * u, py + 3 * u), avoid, 70, 70):
                continue
            for dx, dy in ((1, 0), (0, 1), (2, 1), (1, 2)):
                d.rectangle([px + dx * u, py + dy * u, px + dx * u + u - 1, py + dy * u + u - 1], fill=hex2rgb(sc["deco_spark"]))
            break


def make_background(ly, a, assets, rects):
    sc = M.SCHEMES[a.scheme]
    w, h = ly["w"], ly["h"]
    if a.bg == "scene":
        return starfield(assets["scene"], assets["scene_anchor"], w, h, a.bg_scale, a.bg_anchor[0], a.bg_anchor[1], a.bg_shift)
    im = Image.new("RGB", (w, h), hex2rgb(sc["bg"]))
    pixel_deco(im, ly, sc, a.seed, rects)
    return im


# ---- 文字 ----
CSS = """
<link rel="stylesheet" href="file:///{FONTS}">
<style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body { width:{W}px; height:{H}px; overflow:hidden; background:{BG}; font-family:'Noto Sans SC', sans-serif; }
.bgimg { position:absolute; inset:0; background:url({IMG}) center/100% 100% no-repeat; }
.t { position:absolute; left:{X}px; font:900 100px/1 'Noto Sans SC'; letter-spacing:-.01em; white-space:nowrap; {SHADOW}
     -webkit-text-stroke:16px {BG}; paint-order:stroke fill; }   /* 描一圈和底色一样的边（在字下面），挤掉紧贴字边的星点 */
#t1 { top:0; color:{T1}; }
#t2 { top:0; color:{T2}; }
</style>
"""


def line_y(fs, ly, two_lines):
    y1 = ly["y1"] if two_lines else ly["y1"] + 110          # 单行：比两行的第一行低一点，位置不随字号变
    return y1, y1 + 1.08 * fs


def feasible(fs, w1u, w2u, ly, rects, two_lines):
    """字号 fs 下：每行不超出右边界；字框外扩（左右 gap、上下 24 px）后不碰宇航员的任何一格。"""
    y1, y2 = line_y(fs, ly, two_lines)
    boxes = [[ly["x"], y1, ly["x"] + w1u * fs / 100, y1 + fs]]
    if two_lines:
        boxes.append([ly["x"], y2, ly["x"] + w2u * fs / 100, y2 + fs])
    for bx in boxes:
        if bx[2] > ly["right"] or box_hits(bx, rects, ly["gap"], 24):
            return False
    return True


def solve_fs(w1u, w2u, ly, rects, two_lines):
    """w1u / w2u = 两行在 100 px 字号下的宽度。从 fs_max 往下逐档（2 px）试，取最大的可行字号；都不行就 60（外面报警）。"""
    for fs in range(ly["fs_max"], 59, -2):
        if feasible(fs, w1u, w2u, ly, rects, two_lines):
            return fs
    return 60


def text_html(ly, a, bg_im=None):
    sc = M.SCHEMES[a.scheme]
    two = bool(a.line2.strip())
    css = CSS
    shadow = "text-shadow:0 8px 40px rgba(0,0,0,.7);" if a.scheme == "night" else ""
    img = uri_png(bg_im) if bg_im is not None else ""
    for k, v in dict(FONTS=str(FONTS_CSS).replace("\\", "/"), W=ly["w"], H=ly["h"], BG=sc["bg"], X=ly["x"], T1=sc["t1"], T2=sc["t2"], SHADOW=shadow, IMG=img).items():
        css = css.replace("{" + k + "}", str(v))
    body = ('<div class="bgimg"></div>' if bg_im is not None else "") + f'<div id="t1" class="t">{html.escape(a.line1)}</div>' + (f'<div id="t2" class="t">{html.escape(a.line2)}</div>' if two else "")
    return "<!doctype html><html><head><meta charset='utf-8'></head><body>" + css + body + "</body></html>"


def measure_text(pw_browser, ly, a):
    """两行在 100 px 字号下的宽度（和封面一样的字体样式）。"""
    pg = pw_browser.new_page(viewport={"width": ly["w"], "height": ly["h"]})
    pg.set_content(text_html(ly, a))
    pg.evaluate("document.fonts.ready.then(() => true)")
    pg.wait_for_timeout(700)
    w = pg.evaluate("""() => ['t1', 't2'].map(id => { const e = document.getElementById(id); return e ? e.getBoundingClientRect().width : 0; })""")
    pg.close()
    return w


def render_page(pw_browser, ly, a, bg_im, fs, out_png):
    two = bool(a.line2.strip())
    pg = pw_browser.new_page(viewport={"width": ly["w"], "height": ly["h"]})
    pg.set_content(text_html(ly, a, bg_im))
    pg.evaluate("document.fonts.ready.then(() => true)")
    pg.wait_for_timeout(700)
    y1, y2 = [round(v) for v in line_y(fs, ly, two)]
    boxes = pg.evaluate("""([fs, y1, y2]) => { const out = {}; for (const [id, top] of [['t1', y1], ['t2', y2]]) { const e = document.getElementById(id); if (!e) continue;
        e.style.fontSize = fs + 'px'; e.style.top = top + 'px'; const r = e.getBoundingClientRect(); out[id] = [r.left, r.top, r.left + r.width, r.top + r.height]; } return out; }""", [fs, y1, y2])
    pg.wait_for_timeout(300)
    pg.screenshot(path=str(out_png))
    pg.close()
    return boxes


def load_assets(a):
    out = {}
    need_scene = a.bg == "scene"
    if need_scene:
        if not (ASSETS / "scene_clean.png").exists() or not (ASSETS / "sprite.json").exists():
            sys.exit("--bg scene 要 assets/scene_clean.png 和 sprite.json：先跑 scripts/build_assets.py（或改用 --bg pixel）")
        out["scene"] = Image.open(ASSETS / "scene_clean.png").convert("RGB")
        out["scene_anchor"] = json.loads((ASSETS / "sprite.json").read_text(encoding="utf-8"))["scene_anchor"]
    return out


def main():
    ap = argparse.ArgumentParser(description="Claude Code相关封面（Claude 像素宇航员 + 品牌色背景）")
    ap.add_argument("--line1", required=True)
    ap.add_argument("--line2", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="C")
    ap.add_argument("--scheme", default="night", choices=list(M.SCHEMES))
    ap.add_argument("--pose", default="float")
    ap.add_argument("--flip", action="store_true")
    ap.add_argument("--eyes", default=None, choices=[None, "happy", "wink"])
    ap.add_argument("--select", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--cell-16x9", type=int, default=LAYOUT["16x9"]["cell"])
    ap.add_argument("--cell-4x3", type=int, default=LAYOUT["4x3"]["cell"])
    ap.add_argument("--min-cell-16x9", type=int, default=LAYOUT["16x9"]["min_cell"], help="自动缩小宇航员时每格的保底（默认 16 = 身体宽 20%；再小到 13 以下身体宽就 < 17%，验收不过）")
    ap.add_argument("--min-cell-4x3", type=int, default=LAYOUT["4x3"]["min_cell"], help="同上，4:3（默认 12）")
    ap.add_argument("--mpos-16x9", type=pair, default=LAYOUT["16x9"]["mpos"])
    ap.add_argument("--mpos-4x3", type=pair, default=LAYOUT["4x3"]["mpos"])
    ap.add_argument("--bg", default=None, choices=[None, "scene", "pixel"])
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--no-fit", dest="fit", action="store_false", help="不自动缩小宇航员（默认：字号低于 fs_fit 时把宇航员缩小一格再试）")
    ap.add_argument("--bg-scale", type=float, default=3.0)
    ap.add_argument("--bg-anchor", type=pair, default=(0.72, 0.64))
    ap.add_argument("--bg-shift", type=pair, default=(0.0, 0.0))
    a = ap.parse_args()
    if a.bg is None:
        a.bg = "scene" if (a.scheme == "night" and (ASSETS / "scene_clean.png").exists()) else "pixel"
    if a.bg == "scene" and a.scheme != "night":
        sys.exit("官方星空截图是深色的，--bg scene 只能配 --scheme night")
    if a.cell_16x9 < 16:
        print(f"⚠ 16:9 每格 {a.cell_16x9} px < 16：宇航员比用户要的“大一点”小")
    if not FONTS_CSS.exists():
        print(f"⚠ 找不到字体 {FONTS_CSS}，会退回系统字体，字形会变")
    assets = load_assets(a)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ratios = {"16x9": dict(LAYOUT["16x9"], cell=a.cell_16x9, min_cell=a.min_cell_16x9, mpos=a.mpos_16x9),
              "4x3": dict(LAYOUT["4x3"], cell=a.cell_4x3, min_cell=a.min_cell_4x3, mpos=a.mpos_4x3)}
    results = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        w1u, w2u = measure_text(b, ratios["16x9"], a)
        two = bool(a.line2.strip())
        for name, ly in ratios.items():
            cell0 = ly["cell"]
            while True:
                ly = dict(ly, cell=cell0)
                sp, origin, bbox, rects, shift = place_mascot(ly, a)
                fs = solve_fs(w1u, w2u, ly, rects, two)
                if not a.fit or fs >= ly["fs_fit"] or cell0 <= min(ly["min_cell"], ly["cell"]):
                    break
                cell0 -= 1
            warns = []
            if cell0 != ratios[name]["cell"]:
                warns.append(f"字和宇航员（连道具）抢横向空间：宇航员每格从 {ratios[name]['cell']} 缩到 {cell0} px，字号才能到 {fs}（想保持大宇航员就换动作、--flip，或缩短封面字）")
            if fs < 130:
                warns.append(f"字号只剩 {fs}：封面字太长（放不下就缩到 12 个字以内，或换个动作）")
            bg = make_background(ly, a, assets, rects + [tuple(bbox)])
            bg.paste(sp.im, origin, sp.im)
            png = out / f"封面_{a.name}_{name}.png"
            boxes = render_page(b, ly, a, bg, fs, png)
            meta = {"size": [ly["w"], ly["h"]], "scheme": a.scheme, "line1": a.line1, "line2": a.line2, "font_size": fs,
                    "text_boxes": boxes, "safe_x": list(ly["safe"]) if name == "16x9" else [0, ly["w"]],
                    "colors": {"bg": M.SCHEMES[a.scheme]["bg"], "t1": M.SCHEMES[a.scheme]["t1"], "t2": M.SCHEMES[a.scheme]["t2"]},
                    "mascot": {"pose": a.pose, "flip": a.flip, "eyes": a.eyes, "cell": ly["cell"], "origin": list(origin), "bbox": [round(v, 1) for v in bbox],
                               "width_frac": round((bbox[2] - bbox[0]) / ly["w"], 4), "body_width_frac": round(24 * ly["cell"] / ly["w"], 4), "shifted": list(shift)},
                    "background": {"mode": a.bg, "seed": a.seed, "scale": a.bg_scale, "anchor": a.bg_anchor, "shift": a.bg_shift}}
            png.with_suffix(".meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
            results[name] = png
            print(f"-> {png}  字号 {fs}，宇航员每格 {ly['cell']} px（身体宽 {meta['mascot']['body_width_frac'] * 100:.1f}%）" + (f"，整体挪了 {shift}" if shift != (0, 0) else ""))
            for w in warns:
                print("  ⚠", w)
        b.close()
    if a.select:
        for name, png in results.items():
            dst = out / f"封面_选定_{name}.png"
            if dst.exists() and not a.force:
                print(f"已有 {dst.name}，没覆盖（要覆盖加 --force）")
                continue
            shutil.copy2(png, dst)
            print("选定 ->", dst)
    print("下一步：python check_cover.py", results["16x9"], "和", results["4x3"], "，再打开两张图看一眼")


if __name__ == "__main__":
    main()
