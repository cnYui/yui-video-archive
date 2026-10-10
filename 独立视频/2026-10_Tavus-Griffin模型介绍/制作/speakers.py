# -*- coding: utf-8 -*-
r"""按音高区分说话人（男声 / 女声）：把词级转写里的词按连续音高分组，打印每一段是谁在说。

  python speakers.py <视频.mp4> <词级转写.json> [--split 165]

自相关法估每 30 ms 一帧的基频，取每个词的中位数；高于 --split Hz 记 F（女），否则 M（男）。只用来给对白字幕标说话人，粗，要对着画面核一遍。
"""
import argparse
import json
import subprocess

import numpy as np


def load_audio(path, sr=16000):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32), sr


def f0_frames(x, sr, fmin=70, fmax=400, win=0.04, hop=0.01):
    n, h = int(win * sr), int(hop * sr)
    lo, hi = int(sr / fmax), int(sr / fmin)
    out = []
    for i in range(0, len(x) - n, h):
        f = x[i:i + n] * np.hanning(n)
        if np.sqrt((f ** 2).mean()) < 0.004:
            out.append(0.0)
            continue
        ac = np.correlate(f, f, "full")[n - 1:]
        ac = ac / (ac[0] + 1e-9)
        seg = ac[lo:hi]
        k = int(seg.argmax())
        out.append(sr / (k + lo) if seg[k] > 0.35 else 0.0)
    return np.array(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("words")
    ap.add_argument("--split", type=float, default=165.0)
    a = ap.parse_args()
    x, sr = load_audio(a.video)
    f0 = f0_frames(x, sr)
    words = json.loads(open(a.words, encoding="utf-8").read())
    lab = []
    for w in words:
        seg = f0[int(w["s"] * 100): int(w["e"] * 100) + 1]
        seg = seg[seg > 0]
        med = float(np.median(seg)) if len(seg) >= 2 else 0.0
        lab.append((w, med))
    # 连续同一说话人的词并成一段（无音高的词沿用前一个）
    runs, cur, last = [], None, None
    for w, m in lab:
        who = ("F" if m > a.split else "M") if m else last
        last = who or last
        if cur is None or who != cur["who"]:
            cur = {"who": who, "s": w["s"], "e": w["e"], "t": [w["w"]], "f": [m]}
            runs.append(cur)
        else:
            cur["e"] = w["e"]
            cur["t"].append(w["w"])
            cur["f"].append(m)
    for r in runs:
        fs = [v for v in r["f"] if v]
        print(f"[{r['s']:6.2f}–{r['e']:6.2f}] {r['who'] or '?'} ({np.median(fs) if fs else 0:5.0f} Hz) {''.join(r['t']).strip()}")


if __name__ == "__main__":
    main()
