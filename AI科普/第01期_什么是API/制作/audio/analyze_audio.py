# -*- coding: utf-8 -*-
"""检查 bgm.wav / sfx：波形、短时电平、频谱图、平均频谱 → bgm_analysis.png / sfx_analysis.png；统计值打印为 JSON。"""
import os
import json
import numpy as np
from scipy import signal as sig
from scipy.io import wavfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.dirname(os.path.abspath(__file__))


def dbfs(x):
    return 20 * np.log10(np.maximum(x, 1e-12))


def load(name):
    sr, x = wavfile.read(os.path.join(OUT, name))
    return sr, x.astype(np.float64) / 32768.0


def stats(x, sr):
    ch = {}
    for i, n in enumerate("LR"):
        c = x[:, i]
        ch[n] = {
            "peak_dBFS": round(float(dbfs(np.max(np.abs(c)))), 2),
            "rms_dBFS": round(float(dbfs(np.sqrt(np.mean(c ** 2)))), 2),
            "dc_offset": float(f"{np.mean(c):.2e}"),
            "clipped_samples": int(np.sum(np.abs(c) >= 32767 / 32768)),
        }
    return {"duration_s": round(len(x) / sr, 3), "channels": ch}


def main():
    sr, x = load("bgm.wav")
    st = stats(x, sr)
    mono = x.mean(axis=1)

    # 3 s 窗口短时 RMS（1 s 步进），只统计淡入淡出之外的区间
    win, hop = 3 * sr, sr
    idx = np.arange(0, len(mono) - win, hop)
    st_rms = np.array([np.sqrt(np.mean(mono[i:i + win] ** 2)) for i in idx])
    t_rms = (idx + win / 2) / sr
    body = (t_rms > 6) & (t_rms < len(mono) / sr - 6)
    st_db = dbfs(st_rms[body])
    st["short_term_rms_3s"] = {
        "min_dBFS": round(float(st_db.min()), 2),
        "max_dBFS": round(float(st_db.max()), 2),
        "std_dB": round(float(st_db.std()), 2),
        "range_first_430s_dB": round(float(np.ptp(dbfs(st_rms[(t_rms > 6) & (t_rms < 430)]))), 2),
    }
    st["crest_factor_dB"] = round(float(dbfs(np.max(np.abs(mono))) - dbfs(np.sqrt(np.mean(mono ** 2)))), 2)

    fig, ax = plt.subplots(4, 1, figsize=(16, 15), gridspec_kw={"height_ratios": [1.1, 0.9, 1.4, 1.0]})
    fig.suptitle("bgm.wav  —  %.1f s, %d Hz, stereo 16-bit" % (len(x) / sr, sr), fontsize=14)

    # 1 波形包络
    blk = int(0.05 * sr)
    nb = len(x) // blk
    for i, (n, col) in enumerate(zip("LR", ["#4A6FD0", "#E2463F"])):
        c = x[:nb * blk, i].reshape(nb, blk)
        tb = (np.arange(nb) + 0.5) * blk / sr
        ax[0].fill_between(tb, c.min(1), c.max(1), color=col, alpha=0.45, lw=0, label=n)
    ax[0].axhline(1, color="k", lw=0.6, ls="--")
    ax[0].axhline(-1, color="k", lw=0.6, ls="--")
    ax[0].set_ylim(-1.05, 1.05)
    ax[0].set_xlim(0, len(x) / sr)
    ax[0].set_ylabel("amplitude")
    ax[0].set_title("waveform (min/max per 50 ms); dashed = full scale; peak L %.1f / R %.1f dBFS"
                    % (st["channels"]["L"]["peak_dBFS"], st["channels"]["R"]["peak_dBFS"]))
    ax[0].legend(loc="upper right")

    # 2 短时电平
    ax[1].plot(t_rms, dbfs(st_rms), color="#141414", lw=1.2, label="RMS 3 s window")
    for t0, t1, lab in [(141, 237, "high decor"), (234, 294, "perc 20%"), (399, 465, "high decor")]:
        ax[1].axvspan(t0, t1, color="#F6C945" if "decor" in lab else "#F2A0BD", alpha=0.25)
        ax[1].text((t0 + t1) / 2, dbfs(st_rms).max() + 1.2, lab, ha="center", fontsize=9)
    ax[1].axvline(435.7, color="#FF4F1A", ls=":", lw=1)
    ax[1].text(436.5, dbfs(st_rms).min() + 1, "video end 435.7 s", color="#FF4F1A", fontsize=9)
    ax[1].set_xlim(0, len(x) / sr)
    ax[1].set_ylim(dbfs(st_rms[body]).min() - 6, dbfs(st_rms).max() + 3)
    ax[1].set_ylabel("dBFS")
    ax[1].set_title("short-term level: body range %.1f..%.1f dBFS, std %.2f dB"
                    % (st_db.min(), st_db.max(), st_db.std()))
    ax[1].grid(alpha=0.3)

    # 3 频谱图
    f, t, S = sig.spectrogram(mono.astype(np.float32), fs=sr, nperseg=4096, noverlap=2048, window="hann")
    keep = (f >= 20) & (f <= 16000)
    im = ax[2].pcolormesh(t, f[keep], 10 * np.log10(S[keep] + 1e-14), shading="auto", cmap="magma",
                          vmin=-130, vmax=-50)
    ax[2].set_yscale("log")
    ax[2].set_ylim(30, 16000)
    ax[2].set_ylabel("Hz")
    ax[2].set_title("spectrogram (mono, log freq)")
    fig.colorbar(im, ax=ax[2], pad=0.01, label="dB")

    # 4 平均频谱
    for i, (n, col) in enumerate(zip("LR", ["#4A6FD0", "#E2463F"])):
        fw, P = sig.welch(x[:, i], fs=sr, nperseg=16384)
        ax[3].semilogx(fw[1:], 10 * np.log10(P[1:] + 1e-20), color=col, lw=1, label=n)
    ax[3].axvspan(1000, 4000, color="#6E6A63", alpha=0.12)
    ax[3].text(2000, ax[3].get_ylim()[1] - 8, "speech presence 1-4 kHz", ha="center", fontsize=9)
    ax[3].set_xlim(20, 20000)
    ax[3].set_xlabel("Hz")
    ax[3].set_ylabel("dB/Hz")
    ax[3].set_title("long-term average spectrum (Welch)")
    ax[3].grid(alpha=0.3, which="both")
    ax[3].legend()
    ax[3].set_ylim(-150, None)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "bgm_analysis.png"), dpi=80)
    plt.close(fig)

    # SFX
    fig, ax = plt.subplots(2, 2, figsize=(14, 7))
    res = {"bgm": st}
    for j, name in enumerate(["sfx_pop.wav", "sfx_tick.wav"]):
        sr2, y = load(name)
        res[name] = stats(y, sr2)
        tt = np.arange(len(y)) / sr2 * 1000
        ax[0, j].plot(tt, y[:, 0], color="#141414", lw=0.8)
        ax[0, j].set_ylim(-1, 1)
        ax[0, j].set_title("%s  %.0f ms  peak %.1f dBFS" % (name, len(y) / sr2 * 1000, res[name]["channels"]["L"]["peak_dBFS"]))
        ax[0, j].set_xlabel("ms")
        fw, P = sig.welch(y[:, 0], fs=sr2, nperseg=1024)
        ax[1, j].semilogx(fw[1:], 10 * np.log10(P[1:] + 1e-20), color="#FF4F1A")
        ax[1, j].set_xlim(50, 20000)
        ax[1, j].grid(alpha=0.3, which="both")
        ax[1, j].set_xlabel("Hz")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "sfx_analysis.png"), dpi=80)
    plt.close(fig)
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
