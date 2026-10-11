# -*- coding: utf-8 -*-
"""口型 / 配音对齐检查：每帧口型（0/1/2）和成片音频里配音能量的相关性随时间偏移（帧）的变化，最佳偏移应该是 0；再抽成片的第 0 帧和几处帧存成图。

  python qa_sync.py <成片.mp4>
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "tl_v.json").read_text(encoding="utf-8"))
SR = 48000


def main():
    mp4 = Path(sys.argv[1])
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.float32)
    fps, n = T["fps"], T["frames"]
    hop = SR // fps
    k = min(n, len(a) // hop)
    rms = np.sqrt((a[: k * hop].reshape(k, hop) ** 2).mean(1))
    mouth = np.array(T["mouth"][:k], dtype=float)
    best = []
    for lag in range(-8, 9):                       # lag > 0：口型比声音晚 lag 帧
        if lag >= 0:
            x, y = mouth[lag:], rms[: k - lag]
        else:
            x, y = mouth[: k + lag], rms[-lag:]
        best.append((float(np.corrcoef(x, y)[0, 1]), lag))
    print("口型 × 配音能量 相关系数（偏移帧 → 相关）：", "  ".join(f"{l:+d}:{c:.3f}" for c, l in best))
    c, l = max(best)
    print(f"最佳偏移 {l:+d} 帧（{l / fps * 1000:+.0f} ms），相关 {c:.3f}；偏移 0 的相关 {dict((lag, cc) for cc, lag in best)[0]:.3f}")
    print("音频时长", f"{len(a) / SR:.2f}s", "；片长帧数", n, f"（{n / fps:.2f}s）")


if __name__ == "__main__":
    main()
