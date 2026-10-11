# -*- coding: utf-8 -*-
"""录屏联系表：每 N 秒一帧、带时间戳，拼成 6×8 的大图，用来找画面（比如误开的微信）和对内容。

  python sheets.py [--every 2] [--size 384] [编号…]        → sheets/<编号>_<页>.jpg
  python sheets.py --range R1013 120 180 --every 0.5     → sheets/<编号>_<起>-<止>_<页>.jpg（只看一段）
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
sys.path.insert(0, str(EP / "制作" / "02_出镜"))
from ingest import SCR, src_of  # noqa: E402

FONT = r"C\:/Windows/Fonts/arial.ttf"


def sheet(i, every=2.0, size=384, t0=None, t1=None, cols=6, rows=8):
    out = HERE / "sheets"
    out.mkdir(exist_ok=True)
    tag = i if t0 is None else f"{i}_{t0:g}-{t1:g}"
    h = size * 9 // 16
    vf = (f"fps=1/{every},scale={size}:{h},"
          f"drawtext=fontfile='{FONT}':text='%{{pts\\:hms}}':x=4:y=4:fontsize={max(14, size // 20)}:fontcolor=yellow:box=1:boxcolor=black@0.7,"
          f"tile={cols}x{rows}:padding=4:margin=4:color=white")
    args = ["ffmpeg", "-v", "error", "-y"]
    if t0 is not None:
        args += ["-ss", str(t0), "-to", str(t1), "-copyts"]
    args += ["-i", str(src_of(i)), "-vf", vf, "-q:v", "3", str(out / f"{tag}_%02d.jpg")]
    subprocess.run(args, check=True)
    print("sheet", tag, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    every, size = 2.0, 384
    while a and a[0].startswith("--"):
        if a[0] == "--every":
            every, a = float(a[1]), a[2:]
        elif a[0] == "--size":
            size, a = int(a[1]), a[2:]
        elif a[0] == "--range":
            sheet(a[1], every, size, float(a[2]), float(a[3]), cols=4, rows=6)
            sys.exit()
    for i in (a or list(SCR)):
        sheet(i, every, size)
