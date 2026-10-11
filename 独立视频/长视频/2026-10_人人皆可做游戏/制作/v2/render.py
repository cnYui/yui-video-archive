# -*- coding: utf-8 -*-
"""render.py —— 渲画面（不含字幕和声音）。

  python render.py still 12.5 40 88 ...        每个时刻渲一张静帧 → _check/still_<秒>.png，并拼联系表 _check/sheet.png
  python render.py chunk 20 40 out.mp4         渲 [20, 40) 秒这一段
  python render.py video [--workers 5] [--chunk 20] [--from 0 --to 999]   全部分段多进程渲，拼成 画面.mp4
  python render.py frames 0 311 6              从 0 到 311 秒每 6 秒一张，拼联系表（检查整条的版式）

画面里的一切（版式、时间点）都在 plan.py：build() → Timeline；render 只管把时间线变成帧。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import ui  # noqa: E402
from ui import FPS, H, W  # noqa: E402

CHECK = HERE / "_check"
PARTS = HERE / "_parts"


def build():
    import plan
    return plan.build()


def x264_cmd(out: Path, threads=2, crf=16):
    return ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
            "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-g", "120",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-threads", str(threads), "-movflags", "+faststart", str(out)]


def render_chunk(t0: float, t1: float, out: Path, threads=2):
    T = build()
    i0, i1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    out.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.Popen(x264_cmd(out, threads), stdin=subprocess.PIPE)
    t_start = time.time()
    try:
        for i in range(i0, i1):
            fr = T.frame(i / FPS)
            p.stdin.write(fr.tobytes())
        p.stdin.close()
        p.wait()
    finally:
        T.close()
    return str(out), time.time() - t_start


def _job(args):
    return render_chunk(*args)


def cmd_still(ts, out_dir=None):
    out_dir = Path(out_dir) if out_dir else CHECK
    out_dir.mkdir(exist_ok=True)
    T = build()
    ims = []
    try:
        for t in ts:
            fr = T.frame(t)
            im = Image.fromarray(fr)
            im.save(out_dir / ("still_%07.2f.png" % t))
            ims.append((t, im))
    finally:
        T.close()
    sheet(ims, out_dir / "sheet.png")
    print("ok", [round(t, 2) for t in ts])


def sheet(ims, path, cols=2, tw=1170):
    th = int(tw * H / W)
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 10) + 10), (225, 226, 232))
    d = ImageDraw.Draw(sh)
    f = ui.nsc(24)
    for k, (t, im) in enumerate(ims):
        x, y = 10 + (k % cols) * (tw + 10), 10 + (k // cols) * (th + 10)
        sh.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x + 8, y + 6), "%.2f s" % t, font=f, fill=(255, 255, 0), stroke_width=3, stroke_fill=(0, 0, 0))
    sh.save(path)


def cmd_video(workers, chunk, t_from, t_to, only=None):
    T = build()
    dur = min(T.dur, t_to)
    T.close()
    PARTS.mkdir(exist_ok=True)
    jobs = []
    t = t_from
    k = int(round(t_from / chunk))
    while t < dur - 1e-6:
        e = min(dur, t + chunk)
        jobs.append((t, e, PARTS / ("part_%03d.mp4" % k)))
        t, k = e, k + 1
    todo = [j for i, j in enumerate(jobs) if (only is None or (int(round(j[0] / chunk)) in only))]
    print("共 %.1f 秒，%d 段（这次渲 %d 段），%d 个进程" % (dur - t_from, len(jobs), len(todo), workers), flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        for path, secs in ex.map(_job, todo):
            print("  ok %s %.0f s" % (Path(path).name, secs), flush=True)
    lst = PARTS / "list.txt"
    lst.write_text("".join("file '%s'" % j[2].as_posix() + chr(10) for j in jobs), encoding="utf-8")
    out = HERE / "画面.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    print("done %s  用时 %.0f s" % (out, time.time() - t0))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("still")
    s.add_argument("t", type=float, nargs="+")
    s.add_argument("--out")
    s = sub.add_parser("frames")
    s.add_argument("a", type=float)
    s.add_argument("b", type=float)
    s.add_argument("step", type=float)
    s = sub.add_parser("chunk")
    s.add_argument("a", type=float)
    s.add_argument("b", type=float)
    s.add_argument("out")
    s = sub.add_parser("video")
    s.add_argument("--workers", type=int, default=5)
    s.add_argument("--chunk", type=float, default=20.0)
    s.add_argument("--from", dest="t_from", type=float, default=0.0)
    s.add_argument("--to", dest="t_to", type=float, default=9999.0)
    s.add_argument("--only", default="", help="只重渲这几段（段号，逗号分隔；段 = 起点秒 / 段长），其余沿用 _parts 里已有的")
    a = ap.parse_args()
    if os.environ.get("LOWPRIO"):
        import psutil
        psutil.Process().nice(psutil.IDLE_PRIORITY_CLASS)
    if a.cmd == "still":
        cmd_still(a.t, a.out)
    elif a.cmd == "frames":
        ts = list(np.arange(a.a, a.b, a.step))
        cmd_still(ts)
    elif a.cmd == "chunk":
        print(render_chunk(a.a, a.b, Path(a.out)))
    elif a.cmd == "video":
        only = {int(x) for x in a.only.split(",") if x.strip()} if a.only else None
        cmd_video(a.workers, a.chunk, a.t_from, a.t_to, only)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
