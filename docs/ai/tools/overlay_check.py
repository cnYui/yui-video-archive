# -*- coding: utf-8 -*-
r"""叠加层抽查：把成片里每个叠加层（数字框 / 说明条 / 高亮框 / 页面录屏 / 来源角标）出现中间的那一帧都抽出来，拼成联系表，逐张看有没有盖住素材自带的名牌、角标、标题。

  python overlay_check.py <引擎目录> [--video 成片.mp4] [--out 目录] [--only-from 秒] [--skip-credit]

<引擎目录> = 含 index.html / timeline.js / scenes.js 的那个目录（横版 制作/00_整片、竖屏短视频 制作/00_整片 都行）。
- 叠加层的起止时刻从页面里的 OV 取（Playwright 打开 index.html，读 OV.map(o => [o.t0, o.t1])），所以和渲染用的是同一套时间；
- 取样时刻 = 叠加层淡入完成之后的中间（t0 + 0.7 s 和 (t0 + t1) / 2 里较晚的、但不晚于 t1 − 0.2 s）；0.25 s 之内的取样合并成一张；
- 画面从 --video 抽（默认 <引擎目录>/整片_v1.mp4）；联系表放 --out（默认 <引擎目录>/stills_overlay/）：横版 3 列 × 3 行一张、竖屏 6 列 × 2 行一张。
- --skip-credit：不抽“来源角标”这类每个素材场景都有的叠加层（持续时间 ≥ 场景长度的、且和别的叠加层同一起点的不去重，只靠这个开关粗筛：t1 − t0 ≥ 8 s 的跳过）。

2026-10-05 《不再Review》长视频第一次渲完只看了每场景 3 张静帧，没发现 288 s 的数字框盖住来源角标和幻灯片标题、访谈左下角的“Matt”名牌被说明条盖掉一半；
用这个脚本（当时是临时脚本 ov_times.py + ov_sheet.py）一次抽出来才看到。出整片前后各跑一遍。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

FONT = r"D:\大疆\AI科普\素材\字体\NotoSansSC.ttf"


def overlay_windows(eng):
    with sync_playwright() as p:
        b = p.chromium.launch()
        meta = {"W": 2340, "H": 1080}
        pg = b.new_page(viewport={"width": 2340, "height": 1080})
        pg.goto((eng / "index.html").as_uri())
        pg.evaluate("document.fonts.ready.then(() => true)")
        try:
            meta = pg.evaluate("({W: window.META.W, H: window.META.H})")
        except Exception:
            pass
        ov = pg.evaluate("OV.map((o, i) => ({i, t0: o.t0, t1: o.t1, fast: !!o.fast, layer: o.layer || ''}))")
        b.close()
    return meta, ov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("engine")
    ap.add_argument("--video")
    ap.add_argument("--out")
    ap.add_argument("--only-from", type=float, default=0.0)
    ap.add_argument("--skip-credit", action="store_true")
    a = ap.parse_args()
    eng = Path(a.engine).resolve()
    video = Path(a.video) if a.video else eng / "整片_v1.mp4"
    out = Path(a.out) if a.out else eng / "stills_overlay"
    out.mkdir(parents=True, exist_ok=True)
    meta, ov = overlay_windows(eng)
    W, H = meta["W"], meta["H"]
    samples = []
    for o in sorted(ov, key=lambda o: o["t0"]):
        if o["t1"] < a.only_from:
            continue
        if a.skip_credit and o["t1"] - o["t0"] >= 8.0:
            continue
        t = max(o["t0"] + 0.7, (o["t0"] + o["t1"]) / 2)
        t = min(t, o["t1"] - 0.2)
        t = max(t, o["t0"] + 0.05)
        if samples and abs(samples[-1][0] - t) < 0.25:
            samples[-1][1].append(o["i"])
            continue
        samples.append([t, [o["i"]]])
    print(f"{len(ov)} 个叠加层，抽 {len(samples)} 帧（{W}×{H}）")
    portrait = H > W
    cols, rows = (6, 2) if portrait else (3, 3)
    tw = 300 if portrait else 780
    th = int(tw * H / W)
    font = ImageFont.truetype(FONT, 22)
    frames = []
    for t, ids in samples:
        f = out / f"ov_{t:08.2f}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", str(f)], check=True)
        frames.append((t, ids, f))
    per = cols * rows
    for n in range(0, len(frames), per):
        chunk = frames[n:n + per]
        r = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (tw + 8) + 8, r * (th + 34) + 8), "#C9CDD3")
        d = ImageDraw.Draw(sheet)
        for j, (t, ids, f) in enumerate(chunk):
            x, y = 8 + (j % cols) * (tw + 8), 8 + (j // cols) * (th + 34)
            d.text((x, y), f"{t:.1f}s  OV#{','.join(str(i) for i in ids)}", fill="#111", font=font)
            sheet.paste(Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS), (x, y + 30))
        o = out / f"_sheet_{n // per + 1}.png"
        sheet.save(o)
        print(o)


if __name__ == "__main__":
    main()
