# -*- coding: utf-8 -*-
"""qa_sync.py —— 人声和出镜画面对不对得上：嘴部区域逐帧变化量 × 人声音量，求互相关，看峰值在不在 0 秒附近。
  python qa_sync.py            （只检查 face_tl.mp4 和 人声.wav，不用整片）
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
import voice  # noqa: E402

W, H = 192, 108


def motion(path):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-vf", "scale=%d:%d,format=gray" % (W, H), "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    prev, out = None, []
    nb = W * H
    while True:
        b = p.stdout.read(nb)
        if len(b) < nb:
            break
        f = np.frombuffer(b, np.uint8).astype(np.float32).reshape(H, W)
        roi = f[int(H * 0.45):int(H * 0.85), int(W * 0.25):int(W * 0.75)]       # 嘴和下巴一带
        out.append(0.0 if prev is None else float(np.abs(roi - prev).mean()))
        prev = roi
    return np.array(out)


def main():
    m = motion(ROOT / "face_tl.mp4")
    y, sr = sf.read(str(ROOT / "人声.wav"), always_2d=True)
    y = y.mean(axis=1)
    hop = sr // 60
    n = min(len(m), len(y) // hop)
    env = np.sqrt((y[:n * hop].reshape(n, hop) ** 2).mean(axis=1))
    m = m[:n]
    # 只比有人声的时间
    on = env > 0.01
    a = (env - env[on].mean()) * on
    b = (m - m[on].mean()) * on
    lags = range(-30, 31)
    res = []
    for L in lags:
        if L >= 0:
            c = float(np.dot(a[L:], b[:n - L]))
        else:
            c = float(np.dot(a[:n + L], b[-L:]))
        res.append((c, L))
    best = max(res)
    print("峰值在滞后 %d 帧（%.0f ms；正数 = 声音比嘴部动作晚，下巴动得最快总在声音最响之前，所以几十毫秒的正数是正常的；拿没剪过的原片比，剪前剪后一样就没问题）" % (best[1], best[1] / 60 * 1000))
    for c, L in sorted(res, reverse=True)[:5]:
        print("  lag %3d 帧  相关 %.1f" % (L, c))


main()
