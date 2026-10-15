# -*- coding: utf-8 -*-
"""逐帧渲染：Playwright Chromium 打开 engine/index.html，按 t = n / 30 调 render(t) 后截图成 PNG。

用法：
  python render_frames.py --preview 0 100 250 ...        只渲染指定帧到 制作/preview/（看版式用）
  python render_frames.py --all [--workers 4]             渲染整条到 制作/build/frames/（同一时间只跑一个渲染）
  python render_frames.py --range 0 1000 --workers 4      只渲染 [0, 1000) 帧
  python render_frames.py --beats 0 16 32 ...             渲染这些拍点上的帧（k 为拍序号，取最近的帧）
"""
import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ENGINE = HERE / "engine" / "index.html"
SCRIPT = Path(os.environ["SCRIPT_JSON"]) if os.environ.get("SCRIPT_JSON") else HERE.parent / "台本" / "台本.json"   # SCRIPT_JSON：临时指定别的台本（待审草稿的版式检查用）
FPS = 30
W, H = 2340, 1080


def load_data():
    d = json.loads(SCRIPT.read_text(encoding="utf-8"))
    missing = []
    for lid, L in d["logos"].items():
        f = L.get("file")
        if f:
            p = HERE / "assets" / "logos" / f
            if p.exists():
                L["file"] = p.as_uri()
            else:
                missing.append(lid)
                L["file"] = None
    d["_missing_logos"] = missing
    return d


def worker(frames, outdir, data, wid):
    outdir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--force-device-scale-factor=1", "--font-render-hinting=none", "--disable-lcd-text"])
        ctx = b.new_context(viewport={"width": W, "height": H}, device_scale_factor=1)
        page = ctx.new_page()
        page.add_init_script("window.DATA = " + json.dumps(data, ensure_ascii=False) + ";")
        page.goto(ENGINE.as_uri())
        page.evaluate("window.__ready")
        t0 = time.time()
        for i, n in enumerate(frames):
            page.evaluate(f"render({n / FPS!r})")
            page.screenshot(path=str(outdir / f"f_{n:05d}.png"), type="png")
            if wid == 0 and i % 100 == 0:
                print(f"[w0] {i}/{len(frames)}  {time.time() - t0:.0f}s", flush=True)
        b.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", nargs="*", type=int)
    ap.add_argument("--beats", nargs="*", type=float)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--range", nargs=2, type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    ap.add_argument("--force", action="store_true", help="覆盖已有的帧（默认跳过，断点续跑）")
    a = ap.parse_args()
    data = load_data()
    if data["_missing_logos"]:
        print("缺 logo 文件（用字母占位）：", ", ".join(data["_missing_logos"]))
    total = math.ceil(data["dur"] * FPS)   # 视频略长于音轨，encode 时 -shortest 对齐
    if a.beats:
        beat = 60 / data["bpm"]
        frames = sorted({min(total - 1, round((data["t0"] + k * beat) * FPS)) for k in a.beats})
        outdir = Path(a.out) if a.out else HERE / "preview"
        worker(frames, outdir, data, 0)
        print("done", len(frames))
        return
    if a.preview is not None and not a.all and not a.range:
        outdir = Path(a.out) if a.out else HERE / "preview"
        worker(a.preview, outdir, data, 0)
        print("done", len(a.preview))
        return
    lo, hi = (a.range if a.range else (0, total))
    frames = list(range(lo, min(hi, total)))
    outdir = Path(a.out) if a.out else HERE / "build" / "frames"
    # 已渲染的跳过（断点续跑）
    if not a.force:
        frames = [n for n in frames if not (outdir / f"f_{n:05d}.png").exists()]
    print(f"总帧数 {total}，待渲染 {len(frames)}，{a.workers} 路并行", flush=True)
    chunks = [frames[i::a.workers] for i in range(a.workers)]
    procs = [Process(target=worker, args=(ch, outdir, data, i)) for i, ch in enumerate(chunks) if ch]
    t0 = time.time()
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print(f"全部完成，用时 {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
