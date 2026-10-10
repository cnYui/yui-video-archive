# -*- coding: utf-8 -*-
"""出镜（DJI）和录屏（OpenScreen）对轴：两边录的是同一段话，用音频互相关算偏移。

  python sync.py            → 每段出镜对每段录屏做粗对齐（10 ms 包络互相关），挑最像的；
                              再在重叠区按 20 s 窗口逐段细对齐（16 kHz GCC-PHAT），看有没有漂移 / 断档。
                              结果写 sync.json：lag = 录屏时间 − 出镜时间（同一个声音）。
"""
import json
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfiltfilt, fftconvolve

HERE = Path(__file__).resolve().parent
CAM = ["0155", "0156", "0158", "0159", "0160", "0161", "0162"]
SCR = ["R0945", "R0948", "R1013", "R1029", "R1036", "R1041", "R1046"]
SR = 16000


def load(i):
    sr, x = wavfile.read(HERE / "audio16" / f"{i}.wav")
    assert sr == SR
    return x.astype(np.float32) / 32768.0


SOS = butter(4, [200, 4000], btype="band", fs=SR, output="sos")


def env(x, hop=160):
    """10 ms 帧的对数能量包络，去均值、归一化。"""
    y = sosfiltfilt(SOS, x)
    n = len(y) // hop
    e = np.sqrt((y[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-10)
    e = np.log(e)
    e -= e.mean()
    e /= e.std() + 1e-9
    return e


def xcorr_full(a, b):
    """返回 (lag_frames, peak, ratio)：b 里和 a 对上的位置 = a 的位置 + lag。用重叠长度归一。"""
    c = fftconvolve(b, a[::-1], mode="full")          # 下标 k 对应 lag = k - (len(a) - 1)
    lags = np.arange(len(c)) - (len(a) - 1)
    # 重叠长度
    ov = np.minimum(len(a), np.minimum(len(b), np.minimum(len(a) + lags, len(b) - lags)))
    ok = ov > 1500                                      # 至少重叠 15 s
    cn = np.where(ok, c / np.maximum(ov, 1), -1)
    k = int(np.argmax(cn))
    peak = cn[k]
    # 第二峰（离主峰 2 s 以外）
    mask = np.abs(lags - lags[k]) > 200
    second = cn[mask & ok].max() if (mask & ok).any() else 0
    return int(lags[k]), float(peak), float(peak / max(second, 1e-6)), int(ov[k])


def gcc_phat(a, b, max_shift):
    """a、b 等长片段；返回 b 相对 a 的偏移（样本，正 = b 晚），只在 ±max_shift 里找。"""
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    A = np.fft.rfft(a, n)
    B = np.fft.rfft(b, n)
    R = B * np.conj(A)
    R /= np.abs(R) + 1e-12
    cc = np.fft.irfft(R, n)
    cc = np.concatenate((cc[-max_shift:], cc[: max_shift + 1]))
    k = int(np.argmax(np.abs(cc)))
    # 抛物线插值
    if 0 < k < len(cc) - 1:
        y0, y1, y2 = np.abs(cc[k - 1]), np.abs(cc[k]), np.abs(cc[k + 1])
        d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
    else:
        d = 0
    q = np.sort(np.abs(cc))
    return (k - max_shift + d), float(np.abs(cc[k]) / (q[-50] + 1e-12))


def main():
    audio = {i: load(i) for i in CAM + SCR}
    envs = {i: env(x) for i, x in audio.items()}
    res = {}
    print("粗对齐（每段出镜 × 每段录屏，peak 越大越像）")
    for c in CAM:
        rows = []
        for s in SCR:
            lag, peak, ratio, ov = xcorr_full(envs[c], envs[s])
            rows.append((peak, s, lag, ratio, ov))
        rows.sort(reverse=True)
        line = "  ".join(f"{s}:{p:.2f}(lag {l / 100:+.2f}s, x{r:.1f}, ov {o / 100:.0f}s)" for p, s, l, r, o in rows[:3])
        print(f"{c}: {line}", flush=True)
        best = rows[0]
        res[c] = {"scr": best[1], "lag_coarse": best[2] / 100, "peak": round(best[0], 3), "ratio": round(best[3], 2),
                  "candidates": [{"scr": s, "lag": l / 100, "peak": round(p, 3), "ratio": round(r, 2), "overlap_s": o / 100} for p, s, l, r, o in rows]}

    print("\n细对齐（20 s 窗口，每 10 s 一个；lag = 录屏时间 − 出镜时间）")
    W, HOP, MS = 20 * SR, 10 * SR, int(0.25 * SR)
    for c in CAM:
        r = res[c]
        s = r["scr"]
        a, b = audio[c], audio[s]
        lag0 = int(round(r["lag_coarse"] * SR))
        wins = []
        t = max(0, -lag0)
        while t + W <= len(a) and t + lag0 + W + MS <= len(b):
            if t + lag0 - MS >= 0:
                seg_a = a[t: t + W]
                seg_b = b[t + lag0 - MS: t + lag0 + W + MS]
                # 把 a 补成和 seg_b 一样长，居中
                pad = np.zeros(len(seg_b), np.float32)
                pad[MS: MS + W] = seg_a
                d, q = gcc_phat(pad, seg_b, MS)
                if np.abs(seg_a).max() > 0.01:
                    wins.append({"cam_t": round(t / SR, 2), "lag": round((lag0 + d) / SR, 4), "q": round(q, 1)})
            t += HOP
        r["windows"] = wins
        good = [w for w in wins if w["q"] >= 3]
        if good:
            lags = np.array([w["lag"] for w in good])
            ts = np.array([w["cam_t"] for w in good])
            r["lag"] = round(float(np.median(lags)), 4)
            if len(good) >= 3:
                k, b0 = np.polyfit(ts, lags, 1)
                r["drift_ppm"] = round(k * 1e6, 1)
            r["lag_spread_ms"] = round(float((lags.max() - lags.min()) * 1000), 1)
        print(f"{c} ↔ {s}: coarse {r['lag_coarse']:+.2f}s  fine {r.get('lag')}  spread {r.get('lag_spread_ms')} ms  drift {r.get('drift_ppm')} ppm  "
              f"windows {len(wins)} (good {len(good)})", flush=True)
        for w in wins:
            print(f"    cam {w['cam_t']:7.1f}s  lag {w['lag']:+.4f}s  q {w['q']}")
    (HERE / "sync.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
