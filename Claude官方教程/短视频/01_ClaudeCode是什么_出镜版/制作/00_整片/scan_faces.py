# -*- coding: utf-8 -*-
r"""扫一遍抽好的素材帧，找“讲师的脸”（官方课里讲师出镜的镜头不能用：画面规则 = 只用屏幕 / 动画镜头）。
OpenCV Haar 正脸检测，每 6 帧（0.2 s）看一张，脸宽 ≥ 90 px（素材帧是 1474 宽）才算；连续的合成一段打印：场景 / 成片秒数 / 脸的位置。
  python scan_faces.py        （要先跑过 prep_frames.py）
"""
import json
import sys
from pathlib import Path

import cv2

HERE = Path(__file__).resolve().parent
tl = json.loads((HERE / "timeline.js").read_text(encoding="utf-8")[len("window.TL = "):].rstrip().rstrip(";")) if (HERE / "timeline.js").read_text(encoding="utf-8").startswith("window.TL = ") else None
if tl is None:
    s = (HERE / "timeline.js").read_text(encoding="utf-8")
    tl = json.loads(s[s.index("{"): s.rindex("}") + 1])
fs = (HERE / "frames.js").read_text(encoding="utf-8")
FR = json.loads(fs[fs.index("{"): fs.rindex("}") + 1])
det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
fps = tl["fps"]


def seg_of(t):
    g = None
    for s in tl["segs"]:
        if s["s"] <= t + 1e-6:
            g = s
    return g["id"] if g else "?"


hits = []
for key in ("scr", "scr2"):
    arr = FR.get(key) or []
    for n in range(0, len(arr), 6):
        f = arr[n]
        if not f or f.startswith("card"):
            continue
        im = cv2.imread(str(HERE / "media" / f), cv2.IMREAD_GRAYSCALE)
        if im is None:
            continue
        faces = det.detectMultiScale(im, scaleFactor=1.1, minNeighbors=6, minSize=(90, 90))
        if len(faces):
            hits.append((n / fps, key, seg_of(n / fps), [tuple(map(int, b)) for b in faces]))
if not hits:
    print("没扫到脸")
    sys.exit(0)
runs, cur = [], [hits[0]]
for h in hits[1:]:
    if h[1] == cur[-1][1] and h[0] - cur[-1][0] <= 0.5:
        cur.append(h)
    else:
        runs.append(cur); cur = [h]
runs.append(cur)
for r in runs:
    print(f"{r[0][2]} {r[0][1]} {r[0][0]:.1f}–{r[-1][0]:.1f} s（{len(r)} 张） 脸 {r[0][3][0]}")
print(f"共 {len(runs)} 段疑似有脸")
