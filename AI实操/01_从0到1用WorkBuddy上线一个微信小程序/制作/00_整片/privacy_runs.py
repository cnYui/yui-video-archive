# -*- coding: utf-8 -*-
"""把某一项的打码按连续片段分组（输出帧连续、框位置接近），每段取中间一帧，原图上画框，裁框附近放大看。
  python privacy_runs.py <项>   → privacy/_runs_<项>_N.jpg，并打印每段的帧号、录屏时间、框"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

import privacy_blur as pb

name = sys.argv[1]
seq = json.loads((pb.OUT / "applied.json").read_text(encoding="utf-8"))
fl = pb.frame_list()
rows = []
for n, p, take, t in fl:
    bs = [b for nm, b in seq.get(p, []) if nm == name]
    if bs:
        rows.append((n, p, take, t, bs[0]))
runs = []
for r in rows:
    if runs:
        last = runs[-1][-1]
        cx0, cy0 = (last[4][0] + last[4][2]) / 2, (last[4][1] + last[4][3]) / 2
        cx1, cy1 = (r[4][0] + r[4][2]) / 2, (r[4][1] + r[4][3]) / 2
        if r[0] - last[0] <= 3 and r[2] == last[2] and abs(cx1 - cx0) < 80 and abs(cy1 - cy0) < 60:
            runs[-1].append(r)
            continue
    runs.append([r])
print(name, len(rows), "帧，", len(runs), "段")
tiles = []
for k, run in enumerate(runs):
    n, p, take, t, box = run[len(run) // 2]
    im = cv2.imread(str(pb.ORIG / Path(p).name)) if (pb.ORIG / Path(p).name).exists() else cv2.imread(str(pb.HERE / "media" / p))
    x0, y0, x1, y1 = [int(v) for v in box]
    cv2.rectangle(im, (x0, y0), (x1, y1), (0, 0, 255), 2)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w = max(x1 - x0, 120) * 3.0
    h = w * 207 / 368
    a0, b0 = int(max(0, cx - w / 2)), int(max(0, cy - h / 2))
    crop = im[b0:int(b0 + h), a0:int(a0 + w)]
    lab = f"#{k} {take} {run[0][3]:.1f}-{run[-1][3]:.1f} n{len(run)}"
    print(lab, "输出帧", run[0][0], "-", run[-1][0], "框", [int(v) for v in box])
    tiles.append((crop, lab))
for i in range(0, len(tiles), 36):
    pb.grid(tiles[i:i + 36], pb.OUT / f"_runs_{name}_{i // 36 + 1}.jpg")
