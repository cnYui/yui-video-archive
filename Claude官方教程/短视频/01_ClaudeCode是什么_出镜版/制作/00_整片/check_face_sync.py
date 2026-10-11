# -*- coding: utf-8 -*-
r"""核对成片里的出镜小窗和口播原片是不是帧对帧：在几个时刻取成片的脸（小窗中心）和 talk_face.mp4 前后 ±8 帧（镜像、缩到同样大小）比，找最像的帧号。
  python check_face_sync.py [成片.mp4]       结果 offset = 0 表示对得上；±1 以内算正常
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

EP = Path(__file__).resolve().parents[2]
VID = Path(sys.argv[1]) if len(sys.argv) > 1 else EP / "ClaudeCode是什么_出镜版_成片.mp4"
FACE = EP / "制作" / "01_口播" / "talk_face.mp4"
TMP = Path(__file__).resolve().parent / "_sync_tmp"
TMP.mkdir(exist_ok=True)
# (时刻 s, 窗口左上角 x, y, 边长)：dual = (40, 1460, 240)；single = (360, 1664, 360)
POINTS = [(36.0, 40, 1460, 240), (120.5, 40, 1460, 240), (300.0, 40, 1460, 240), (420.0, 40, 1460, 240), (500.0, 40, 1460, 240), (541.5, 360, 1664, 360), (565.0, 360, 1664, 360)]


def grab(src, t, vf, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", str(src), "-frames:v", "1", "-vf", vf, str(out)], check=True)
    return np.asarray(Image.open(out).convert("L")).astype(float)


worst = 0
for t, x, y, s in POINTS:
    # 成片里的脸：窗口中央 60%（避开圆角、贴纸）
    c0, cs = int(s * 0.2), int(s * 0.6)
    a = grab(VID, t, f"crop={cs}:{cs}:{x + c0}:{y + c0},scale=48:48", TMP / "a.png")
    n0 = int(round(t * 30))
    best = None
    for k in range(-8, 9):
        n = n0 + k
        # 参考：talk_face 第 n 帧，镜像、缩到 s×s 后同样裁中央 60%
        ref = grab(FACE, n / 30 + 1e-3, f"hflip,scale={s}:{s},crop={cs}:{cs}:{c0}:{c0},scale=48:48", TMP / "b.png")
        d = np.abs(a - ref).mean()
        if best is None or d < best[0]:
            best = (d, k)
    worst = max(worst, abs(best[1]))
    print(f"t={t:6.1f}s  最像的帧偏移 {best[1]:+d}（差 {best[0]:.1f}）")
print("最大偏移", worst, "帧")
