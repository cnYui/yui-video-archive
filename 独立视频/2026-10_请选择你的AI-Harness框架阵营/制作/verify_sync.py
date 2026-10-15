# -*- coding: utf-8 -*-
"""校验成片的卡点：
1) 成片音轨和参考音轨互相关，量化整体偏移（应 ≈ 0）；
2) 逐帧差分找每一页的“落位”帧，对比小节首拍的理论时间（偏差应在 ±1 帧 = 33 ms 内）。
用法：python verify_sync.py <成片.mp4>
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy.signal as sg

HERE = Path(__file__).resolve().parent
REF = HERE.parent / "参考分析" / "ref.mp4"
BPM, T0 = 130.0, 0.503
BEAT = 60 / BPM
FPS = 30


def audio(path, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def env(x, sr=16000, hop=160):
    n = len(x) // hop
    return np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(axis=1))


def main():
    vid = Path(sys.argv[1])
    a, b = audio(REF), audio(vid)
    n = min(len(a), len(b))
    ea, eb = env(a[:n]), env(b[:n])
    ea, eb = ea - ea.mean(), eb - eb.mean()
    xc = sg.correlate(eb, ea, mode="full", method="fft")
    lag = (np.argmax(xc) - (len(ea) - 1)) * 10  # ms（每个包络点 10 ms）
    print(f"音轨：成片 {len(b) / 16000:.3f}s / 参考 {len(a) / 16000:.3f}s，互相关偏移 = {lag:+d} ms（0 = 同步）")

    W, H = 160, 90
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(vid), "-vf", f"fps={FPS},scale={W}:{H}", "-pix_fmt", "gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))      # d[i] = |frame[i+1] - frame[i]|
    print(f"视频：{len(fr)} 帧 = {len(fr) / FPS:.3f}s")
    worst = 0
    data = json.loads((HERE.parent / "台本" / "台本.json").read_text(encoding="utf-8"))
    SB, IB, N = data.get("slide_beats", 16), data.get("intro_beats", 16), len(data["camps"])
    for i in range(1, N + 2):
        k = IB + SB * (i - 1)
        t = T0 + k * BEAT
        f = round(t * FPS)
        if f + 12 >= len(d):
            break
        # 在理论落位帧附近 ±12 帧里，找“位移完成”的帧：最后一个大于阈值的差分之后
        lo, hi = max(0, f - 12), min(len(d) - 1, f + 12)
        seg = d[lo:hi]
        big = np.where(seg > max(2.0, seg.max() * 0.12))[0]
        if len(big) == 0:
            print(f"  第 {i:2d} 页 k={k:3d}  理论 {t:7.3f}s (帧 {f})：附近没有明显画面变化")
            continue
        # 推入动画是 [t-0.25, t+0.05]：第一个大差分应在 f-8 附近，之后随缓动衰减
        first = lo + big[0]
        last_move = lo + big[big <= (f - lo + 3)][-1] if (big <= (f - lo + 3)).any() else lo + big[-1]
        print(f"  第 {i:2d} 页 k={k:3d}  理论落位 {t:7.3f}s (帧 {f})  推入起于帧 {first} ({(first - f) / FPS * 1000:+.0f} ms)，"
              f"最后大位移在帧 {last_move} ({(last_move - f) / FPS * 1000:+.0f} ms)")
        worst = max(worst, abs(last_move - f))
    print(f"最后一次大位移与理论落位的最大偏差 = {worst} 帧")


if __name__ == "__main__":
    main()
