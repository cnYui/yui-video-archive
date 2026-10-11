# -*- coding: utf-8 -*-
"""封面验收：python check_cover.py <封面.png> [<封面2.png> …] [--meta <封面.meta.json>]（可一次给多张；meta 默认取各自同名 .meta.json，make_cover.py 生成；--meta 只配单张）

把“必须有 Claude 像素形象、必须是 Claude 品牌色”做成机器能查的几条；全部通过退出码 0，有一条不过退出码 1。
 1. 尺寸：1920×1080（16:9）或 1440×1080（4:3）
 2. 底色：night 方案四条边亮度中位数 < 45；其他方案四条边的中位颜色和该方案的底色（米白 / 品牌橙 / 淡黄）相差 ≤ 24
 3. 品牌橙（#D97757，容差 12）的像素占 ≥ 1%（宇航员身体；night 方案还有第二行字）；orange 方案本身就是橙底，不查这条
 4. 没有品牌以外的色相：饱和度和亮度都高的像素里，色相不在 8°–62°（橙 – 黄）的不超过 0.05%
 5. Claude 像素宇航员在：按 meta 里的动作 / 格子大小 / 位置把宇航员重新渲染一遍，和成图逐像素对，≥ 95% 一致（说明没被字压住、没被裁）；
    身体宽 ≥ 画面宽的 17%（16:9）/ 18%（4:3）
 6. 16:9 的字和宇航员在 16:10 安全区内（左右各 96 px 里没有该方案的字色 / 品牌橙像素）
这几条不能代替看图：出图后还是要打开两张 PNG 看一眼（字有没有被挤、星点有没有读成标点、宇航员有没有被裁）。
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mascot as M  # noqa: E402

ORANGE = np.array([217, 119, 87])


def hsv(a):
    a = a.astype(float) / 255
    mx, mn = a.max(axis=2), a.min(axis=2)
    d = mx - mn
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = d > 1e-6
    ds = np.where(m, d, 1)
    h = np.zeros_like(mx)
    h = np.where(m & (mx == r), ((g - b) / ds) % 6, h)
    h = np.where(m & (mx == g), (b - r) / ds + 2, h)
    h = np.where(m & (mx == b), (r - g) / ds + 4, h)
    return h * 60, np.where(mx > 0, d / np.where(mx > 0, mx, 1), 0), mx


def check_one(png, meta_arg=None, quiet=False):
    """验收一张封面，返回是否全部通过。quiet = 只在不通过时逐条打印（候选批量出图用）。"""
    png = Path(png)
    meta_p = Path(meta_arg) if meta_arg else png.with_suffix(".meta.json")
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else None
    im = np.asarray(Image.open(png).convert("RGB"))
    H, W = im.shape[:2]
    res, lines = [], []

    def ok(name, cond, detail):
        res.append(bool(cond))
        lines.append(("通过 " if cond else "不通过 ") + name + "：" + detail)

    scheme = meta["scheme"] if meta else "night"
    ok("1 尺寸", (W, H) in [(1920, 1080), (1440, 1080)], f"{W}×{H}")
    border = np.concatenate([im[:12].reshape(-1, 3), im[-12:].reshape(-1, 3), im[:, :12].reshape(-1, 3), im[:, -12:].reshape(-1, 3)])
    if scheme == "night":
        med = float(np.median(border.max(axis=1)))
        ok("2 底色", med < 45, f"night：边缘亮度中位数 {med:.0f}")
    else:
        bg = np.array(M.hex2rgb(M.SCHEMES[scheme]["bg"]))
        med = np.median(border, axis=0)
        diff = float(np.abs(med - bg).max())
        ok("2 底色", diff <= 24, f"{scheme}：边缘中位颜色 {med.astype(int).tolist()} 和底色 {bg.tolist()} 相差 {diff:.0f}")
    near = (np.abs(im.astype(int) - ORANGE).max(axis=2) <= 12)
    if scheme != "orange":
        ok("3 品牌橙占比", near.mean() >= 0.01, f"{near.mean() * 100:.1f}%（#D97757，要 ≥ 1%）")
    h, s, v = hsv(im)
    off = (s > 0.35) & (v > 0.35) & ~((h >= 8) & (h <= 62))
    ok("4 无品牌以外的色相", off.mean() <= 0.0005, f"{off.mean() * 100:.3f}%（饱和像素里色相不在橙–黄的）")
    if meta:
        m = meta["mascot"]
        cv = M.build(m["pose"], m["flip"], m["eyes"])
        sp = M.render(cv, m["cell"], scheme)
        ox, oy = m["origin"]
        arr = np.asarray(sp.im)
        h2, w2 = arr.shape[:2]
        ys0, xs0 = max(0, -oy), max(0, -ox)
        ys1, xs1 = min(h2, H - oy), min(w2, W - ox)
        sub = arr[ys0:ys1, xs0:xs1]
        got = im[oy + ys0:oy + ys1, ox + xs0:ox + xs1]
        opaque = sub[..., 3] > 0
        match = float((np.abs(got.astype(int) - sub[..., :3].astype(int)).max(axis=2)[opaque] <= 2).mean()) if opaque.any() else 0.0
        need = 0.17 if W == 1920 else 0.18
        bwf = m["body_width_frac"]
        ok("5 Claude 像素宇航员", match >= 0.95 and bwf >= need, f"动作 {m['pose']}，和重新渲染的宇航员逐像素一致 {match * 100:.1f}%（要 ≥ 95%），身体宽 {bwf * 100:.1f}%（要 ≥ {need * 100:.0f}%）")
        if W == 1920:
            sx0, sx1 = meta["safe_x"]
            c = meta["colors"]
            t1, t2 = np.array(M.hex2rgb(c["t1"])), np.array(M.hex2rgb(c["t2"]))
            txt = (np.abs(im.astype(int) - t1).max(axis=2) <= 8) | (np.abs(im.astype(int) - t2).max(axis=2) <= 8)
            if scheme != "orange":
                txt = txt | near                       # 橙色方案底色就是品牌橙，不能把橙色当“字色”数
            bad = int(txt[:, :sx0].sum() + txt[:, sx1:].sum())
            ok("6 16:10 安全区", bad <= 30, f"左右各 {sx0} px 的边里有 {bad} 个字色 / 橙色像素（≤ 30 算过）")
    else:
        lines.append("（没有 meta.json，跳过第 5、6 条）")
    passed = all(res)
    if not (quiet and passed):
        print("\n".join(lines))
    print(("合格" if passed else "有不合格项") + f"  {png.name}")
    return passed


def main():
    ap = argparse.ArgumentParser(description="封面验收：可一次给多张 png（各自读同名 .meta.json）；全部合格退出码 0")
    ap.add_argument("png", nargs="+")
    ap.add_argument("--meta", help="只在检查单张时用；默认同名 .meta.json")
    a = ap.parse_args()
    if a.meta and len(a.png) > 1:
        sys.exit("--meta 只能配一张 png")
    results = []
    for p in a.png:
        if len(a.png) > 1:
            print(f"== {p}")
        results.append(check_one(p, a.meta))
    if len(a.png) > 1:
        print(f"共 {len(results)} 张，{sum(results)} 张合格" + ("" if all(results) else "，有不合格的"))
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
