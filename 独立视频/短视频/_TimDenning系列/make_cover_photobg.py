# -*- coding: utf-8 -*-
"""系列封面（用户 2026-10-05 夜改版）：文章配图（Midjourney 派对图）铺满做背景，标题字直接写在图上。

  python make_cover_photobg.py            6 期全做：旧框版封面挪进 制作/04_封面/旧版_框版/，新封面 候选A / 候选B × 3:4 / 16:9 / 4:3 + 候选总览.png
  python make_cover_photobg.py 2          只做第 2 期
  之后照旧：python D:\\大疆\\短视频\\skill\\short-video\\scripts\\make_cover_framed.py <本期目录> --select A   （只复制 候选A_* → 封面_选定_*，不重出图）

用户原话：“视频封面写 2800万浏览 推特万字长文解读(X)，封面背景图片就用这个图片吧，作为背景然后把标题文字写在图片上”；
第 1 期：“第一期可以写为2800万浏览 推特万字长文解读(一) 这个写入封面中，然后标题则具体的写 …”，第 2 期同样写成 (二)，第 3 期“和上面一样”。
文字三行：2800万浏览 / 推特万字长文 / 解读(N)（第三行橙色）；样式沿用框版封面的大字（白字 + 橙字、墨色粗描边 + 硬投影）和黄贴纸，字压在底部的暗渐变上（也盖住了图下半部分的亮片裙）。
候选 A = 整张图（人脸在上半、字在下半），候选 B = 更紧地裁到中间那位的脸（放大 1.4 倍）。
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, r"D:\大疆\短视频\skill\short-video\scripts")
import make_cover_framed as M  # noqa: E402  复用字体 / 大字 / 贴纸（只有 main() 在 __main__ 里才跑）
import series_data as D  # noqa: E402
from gen_episode import ep_dir  # noqa: E402

SRC = D.MAT / "图片" / "Substack封面_Midjourney_1232x835.jpg"      # 就是用户贴的那张（X 上裁成 1200×480 的长条），Substack 上是 1232×835 的完整版
SIZES = {"3x4": (1080, 1440), "16x9": (1920, 1080), "4x3": (1440, 1080)}
CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六"}
VARIANTS = {"A": dict(zoom=1.0, fx=0.46, fy=0.40, note="整张配图铺满，字压在下半部（推荐）"),
            "B": dict(zoom=1.4, fx=0.43, fy=0.28, note="更紧地裁到中间那位的脸，字压在下半部")}


def cover_text(n):
    return ["2800万浏览", "推特万字长文", f"解读({CN[n]})"]


def build(kind, n, v):
    W, H = SIZES[kind]
    s = M.SS
    img = Image.open(SRC).convert("RGB")
    iw, ih = img.size
    asp = W / H
    z = v["zoom"]
    if iw / ih > asp:
        ch = ih / z
        cw = ch * asp
    else:
        cw = iw / z
        ch = cw / asp
    cx, cy = v["fx"] * iw, v["fy"] * ih
    x0 = min(max(cx - cw / 2, 0), iw - cw)
    y0 = min(max(cy - ch / 2, 0), ih - ch)
    bg = img.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W * s, H * s), Image.LANCZOS)
    # 暗渐变：整体压暗一点 + 下半部渐黑（字压在上面）；16:9 再加左边（字靠左）
    ys = np.linspace(0, 1, H * s, dtype=np.float32)[:, None]
    a = np.clip((ys - 0.28) / 0.72, 0, 1) ** 1.15 * 0.90
    if kind == "16x9":
        xs = np.linspace(0, 1, W * s, dtype=np.float32)[None, :]
        a = np.maximum(a, np.clip((0.60 - xs) / 0.60, 0, 1) ** 1.2 * 0.62)
    arr = np.asarray(bg, np.float32) * 0.86 * (1 - a[..., None])
    cv = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    lines = cover_text(n)
    if kind == "16x9":
        avail, left, align, fs_max, bottom = 1000, 110, "left", 176, 90
    elif kind == "3x4":
        avail, left, align, fs_max, bottom = W - 140, 70, "center", 176, 130
    else:
        avail, left, align, fs_max, bottom = W - 140, 70, "center", 150, 70
    fs = M.measure(lines, avail, fs_max)[0]
    bh = fs * 1.14 * len(lines)
    top = H - bottom - bh
    M.hook_text(cv, lines, 2, left, top, avail, fs_max, align=align)
    M.draw_sticker(cv, "Tim Denning", (1810 if kind == "16x9" else W - 60), (110 if kind == "16x9" else 100), 1.15)
    return cv.resize((W, H), Image.LANCZOS), f"大字 {fs} px"


def main():
    nums = [int(a) for a in sys.argv[1:]] or [e["num"] for e in D.EPISODES]
    for n in nums:
        ep = next(e for e in D.EPISODES if e["num"] == n)
        d = ep_dir(ep) / "制作" / "04_封面"
        old = d / "旧版_框版"
        if not old.exists() and any(d.glob("候选*_*.png")):
            old.mkdir()
            for f in list(d.glob("候选*_*.png")) + list(d.glob("候选总览.png")) + list(d.glob("封面_选定_*.png")) + [d / "candidates_framed.json"]:
                if f.exists():
                    shutil.move(str(f), str(old / f.name))
        res = {}
        for vid, v in VARIANTS.items():
            for kind in SIZES:
                im, info = build(kind, n, v)
                im.save(d / f"候选{vid}_{kind}.png")
                res[(vid, kind)] = im
        # 总览：每个候选一行（3:4 / 16:9 / 4:3）
        from PIL import ImageDraw
        th = {"3x4": (330, 440), "16x9": (782, 440), "4x3": (587, 440)}
        sheet = Image.new("RGB", (40 + sum(t[0] for t in th.values()) + 40, len(VARIANTS) * 500 + 20), (232, 232, 232))
        dr = ImageDraw.Draw(sheet)
        lab = M.vfont(30, 700)
        y = 20
        for vid, v in VARIANTS.items():
            dr.text((20, y), f"候选 {vid}{'（推荐）' if vid == 'A' else ''}  ·  {v['note']}", font=lab, fill=M.INK)
            x = 20
            for kind in SIZES:
                t = res[(vid, kind)].copy()
                t.thumbnail(th[kind])
                sheet.paste(t, (x, y + 46))
                x += th[kind][0] + 20
            y += 500
        sheet.save(d / "候选总览.png")
        print(f"第 {n} 期：{d}（候选 A / B × 3 比例 + 候选总览.png）")


if __name__ == "__main__":
    main()
