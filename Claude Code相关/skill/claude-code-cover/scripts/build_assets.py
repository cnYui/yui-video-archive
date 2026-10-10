# -*- coding: utf-8 -*-
"""从官方场景截图（assets/scene_src/s6_0..3.png）里抠出 Claude 像素宇航员（4 个姿势）和“没有宇航员的星空”，并记下品牌色。

  python build_assets.py

产出（都在 assets/，png 不进 git，丢了就重跑这个脚本；官方改了插画先跑 capture_scene.py）：
  astronaut_f0..3.png   带透明度的宇航员小图（RGBA，680×590，6 倍像素）：橙色身体 + 头盔浅灰线 + 白色高光 + 黄色小星光，
                        外面一圈和底色一样的暗边（贴到星空上能挤掉紧贴边缘的星点），眼睛的洞补成底色
  scene_clean.png       第 0 帧擦掉宇航员后的整幅星空（8550×4056）
  sprite.json           抠图窗口、锚点（宇航员重心）、主体范围（身体 + 头盔，不含小星光）
  brand.json            品牌色（取自 claude.dev 深色主题：--bg #141413、正文 #FAF9F5、--accent #d97757、--accent-deep #c15f3c）

做法要点：宇航员 = 橙色身体（R>170, 80<G<150, B<120）的重心附近 680×590 的窗口；窗口里“有颜色（max−min>30）或很亮（>175）”的像素
是宇航员（橙、黄、白、浅灰），灰色星点亮度 ≤ 140 不会被选中；向外胀 10 px，从窗口角上灌水，灌不到的（眼睛）补上。
注意：整幅 8550×4056 图别转 int64（要 800 MB），用 uint8 比较。
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
SRC = ASSETS / "scene_src"
DSF = 6
LEFT_RIGHT, UP, DOWN = 340, 330, 260          # 窗口：重心左右各 340、上 330、下 260（6 倍像素）


def hex_of(rgb):
    return "#%02X%02X%02X" % tuple(int(v) for v in rgb)


def extract(img):
    a = np.asarray(img)
    body = (a[..., 0] > 170) & (a[..., 1] > 80) & (a[..., 1] < 150) & (a[..., 2] < 120)
    ys, xs = np.where(body)
    cx, cy = int(xs.mean()), int(ys.mean())
    bx0, by0, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
    x0, y0, x1, y1 = cx - LEFT_RIGHT, cy - UP, cx + LEFT_RIGHT, cy + DOWN
    win = img.crop((x0, y0, x1, y1))
    w = np.asarray(win).astype(np.int16)
    core = ((w.max(axis=2) - w.min(axis=2)) > 30) | (w.max(axis=2) > 175)
    mask = Image.fromarray((core * 255).astype(np.uint8), "L").filter(ImageFilter.MaxFilter(21))
    fill = mask.copy()
    ImageDraw.floodfill(fill, (0, 0), 128)
    alpha = np.asarray(mask).copy()
    alpha[np.asarray(fill) == 0] = 255
    bg = tuple(int(v) for v in a[8, 8])
    rgb = np.where(core[..., None], w, np.array(bg)).astype(np.uint8)
    sprite = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    # 主体范围（窗口坐标）= 橙色身体 + 头盔（浅灰 / 白，饱和度低、亮度高）的外框；黄色小星光不算
    wb = (w[..., 0] > 170) & (w[..., 1] > 80) & (w[..., 1] < 150) & (w[..., 2] < 120)
    light = (w.max(axis=2) > 175) & ((w.max(axis=2) - w.min(axis=2)) <= 30)
    cy_idx, cx_idx = np.where(wb | light)
    main = [int(cx_idx.min()), int(cy_idx.min()), int(cx_idx.max()), int(cy_idx.max())]
    return dict(sprite=sprite, alpha=Image.fromarray(alpha, "L"), window=[x0, y0, x1, y1], centroid=[cx, cy],
                anchor=[cx - x0, cy - y0], body_bbox=[bx0 - x0, by0 - y0, bx1 - x0, by1 - y0], main_bbox=main, bg=bg, core=core, win=w)


def main():
    frames = sorted(SRC.glob("s6_*.png"))
    if not frames:
        raise SystemExit(f"{SRC} 里没有 s6_*.png：先跑 capture_scene.py")
    poses, first = [], None
    for i, f in enumerate(frames):
        img = Image.open(f).convert("RGB")
        r = extract(img)
        r["sprite"].save(ASSETS / f"astronaut_f{i}.png", optimize=True)
        poses.append({k: r[k] for k in ("window", "centroid", "anchor", "body_bbox", "main_bbox")} | {"file": f"astronaut_f{i}.png", "source": f.name})
        print(f"f{i}: 重心 {r['centroid']}，主体 {r['main_bbox']}，身体宽 {r['body_bbox'][2] - r['body_bbox'][0]} px（6 倍）")
        if i == 0:
            first = (img, r)
    img, r = first
    clean = img.copy()
    x0, y0, x1, y1 = r["window"]
    clean.paste(Image.new("RGB", (x1 - x0, y1 - y0), r["bg"]), (x0, y0), r["alpha"])
    clean.save(ASSETS / "scene_clean.png", optimize=True)
    print("scene_clean.png", clean.size)

    # 品牌色：取样 + 官方页面深色主题的变量
    a = np.asarray(first[0])
    body = (a[..., 0] > 170) & (a[..., 1] > 80) & (a[..., 1] < 150) & (a[..., 2] < 120)
    vals, cnt = np.unique(a[body], axis=0, return_counts=True)
    orange = vals[np.argmax(cnt)]
    w = r["win"]
    light = (w.max(axis=2) > 175) & ((w.max(axis=2) - w.min(axis=2)) <= 30)
    lv, lc = np.unique(w[light].reshape(-1, 3), axis=0, return_counts=True)
    yellow = (w.max(axis=2) - w.min(axis=2) > 60) & (w[..., 1] > 180)
    yv, yc = np.unique(w[yellow].reshape(-1, 3), axis=0, return_counts=True)
    brand = {
        "orange": hex_of(orange),                       # 宇航员身体 = claude.dev 的 --accent #d97757
        "orange_deep": "#C15F3C",                       # claude.dev 的 --accent-deep
        "ivory": "#FAF9F5",                             # claude.dev 深色主题的正文色 rgb(250,249,245)
        "dark": hex_of(r["bg"]),                        # 场景底色 = claude.dev 的 --bg #141413
        "dark_raised": "#1A1A18",                       # --bg-raised
        "helmet": hex_of(lv[np.argmax(lc)]) if len(lv) else "#D0CFC4",
        "sparkle": hex_of(yv[np.argmax(yc)]) if len(yv) else "#F8E0A0",
        "source": "claude.dev 深色主题（2026-10-02 读的 CSS 变量和 getComputedStyle）；宇航员颜色取样自 assets/scene_src/s6_0.png",
        "rule": "封面上只用 orange / ivory / dark 三个主色，加宇航员自带的 helmet 灰和 sparkle 黄；不要引入别的色相",
    }
    sprite_json = {"dsf": DSF, "scene_anchor": poses[0]["centroid"], "scene_size": list(img.size), "poses": poses,
                   "note": "window/anchor/body_bbox/main_bbox 都是 6 倍像素；anchor = 宇航员重心在 astronaut_f*.png 里的位置；scene_anchor = 重心在 scene_clean.png 里的位置"}
    (ASSETS / "brand.json").write_text(json.dumps(brand, ensure_ascii=False, indent=2), encoding="utf-8")
    (ASSETS / "sprite.json").write_text(json.dumps(sprite_json, ensure_ascii=False, indent=2), encoding="utf-8")
    print("brand.json:", brand["orange"], brand["ivory"], brand["dark"], "| helmet", brand["helmet"], "| sparkle", brand["sparkle"])


if __name__ == "__main__":
    main()
