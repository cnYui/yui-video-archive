# -*- coding: utf-8 -*-
"""按分数区间看匹配：python privacy_sheet.py <模板> <低> <高> [张数] [裁切]
裁切=1 时每张只看框附近（放大），否则看整帧缩小。"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
ORIG = HERE / "media" / "_scr_orig"
name, lo, hi = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 36
crop = len(sys.argv) > 5 and sys.argv[5] == "1"
hits = json.loads((HERE / "privacy" / "hits.json").read_text(encoding="utf-8"))
rows = sorted([(p, r[name]) for p, r in hits.items() if name in r and lo <= r[name][0] < hi])
print(len(rows), "张")
pick = [rows[int(i)] for i in np.linspace(0, len(rows) - 1, min(n, len(rows)))] if rows else []
tiles = []
for p, (sc, box) in pick:
    src = ORIG / Path(p).name if (ORIG / Path(p).name).exists() else HERE / "media" / p
    im = cv2.imread(str(src))
    x0, y0, x1, y1 = [int(v) for v in box]
    if crop:
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        w = max(x1 - x0, 120) * 2
        h = w * 9 // 16
        a0, b0 = max(0, cx - w // 2), max(0, cy - h // 2)
        sub = im[b0:b0 + h, a0:a0 + w].copy()
        cv2.rectangle(sub, (x0 - a0, y0 - b0), (x1 - a0, y1 - b0), (0, 0, 255), 2)
        im = sub
    else:
        cv2.rectangle(im, (x0, y0), (x1, y1), (0, 0, 255), 3)
    im = cv2.resize(im, (368, 207), interpolation=cv2.INTER_AREA)
    cv2.putText(im, f"{sc:.2f} {Path(p).stem[:20]}", (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 200, 255), 1)
    tiles.append(im)
cols = 6
rws = max(1, (len(tiles) + cols - 1) // cols)
canvas = np.full((rws * 211 + 4, cols * 372 + 4, 3), 200, np.uint8)
for i, im in enumerate(tiles):
    y, x = 4 + (i // cols) * 211, 4 + (i % cols) * 372
    canvas[y:y + 207, x:x + 368] = im
out = HERE / "privacy" / f"_{name}_{lo:.2f}-{hi:.2f}{'_crop' if crop else ''}.jpg"
cv2.imwrite(str(out), canvas, [cv2.IMWRITE_JPEG_QUALITY, 85])
print(out.name)
