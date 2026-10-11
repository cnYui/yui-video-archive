# -*- coding: utf-8 -*-
"""录屏画面活动度：10 fps、缩到 192×108 灰度，算相邻帧的变化。剪停顿时用来分“画面静止（可以剪）”和“画面在动（加速保留）”。

  python activity.py [编号…]   → activity/<编号>.json：{"fps":10, "diff":[…], "area":[…]}
      diff = 相邻帧平均绝对差（0–255）；area = 变化超过 12 的像素占比（光标移动约 0.001–0.003，整屏切换 > 0.3）
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
sys.path.insert(0, str(EP / "制作" / "02_出镜"))
from ingest import SCR, src_of  # noqa: E402

W, H, FPS = 192, 108, 10


def run(i):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src_of(i)), "-vf", f"fps={FPS},scale={W}:{H}:flags=area,format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, check=True)
    a = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W).astype(np.int16)
    d = np.abs(np.diff(a, axis=0))
    diff = d.mean((1, 2))
    area = (d > 12).mean((1, 2))
    out = HERE / "activity"
    out.mkdir(exist_ok=True)
    (out / f"{i}.json").write_text(json.dumps({"fps": FPS, "n": int(len(a)),
                                               "diff": [round(float(x), 3) for x in diff],
                                               "area": [round(float(x), 5) for x in area]}), encoding="utf-8")
    print(i, len(a), "frames", flush=True)


if __name__ == "__main__":
    for i in (sys.argv[1:] or list(SCR)):
        run(i)
