# -*- coding: utf-8 -*-
"""
原LAI如此 #01「什么是 API」—— 程序化合成音频（无采样、无外部素材）

输出（与本脚本同目录）：
  bgm.wav        整片平缓 lo-fi / 轻爵士垫乐，492 s，44.1 kHz / 立体声 / 16 bit，约 -20 LUFS
  sfx_pop.wav    卡片出现的轻“嗒”，0.12 s
  sfx_tick.wav   打勾提示音，0.26 s

用法：python synth_audio.py [临时目录]
  临时目录只用来放响度测量用的中间文件（默认系统 temp）。
依赖：numpy、scipy；响度用 ffmpeg 的 ebur128 滤镜测量（EBU R128 / BS.1770）。
随机数固定种子，重复运行结果完全一致。
"""
import os
import re
import sys
import json
import tempfile
import subprocess

import numpy as np
from scipy import signal as sig
from scipy.io import wavfile

OUT = os.path.dirname(os.path.abspath(__file__))
TMP = sys.argv[1] if len(sys.argv) > 1 else tempfile.gettempdir()

SR = 44100
BPM = 80.0
BEAT = 60.0 / BPM          # 0.75 s
BAR = 4 * BEAT             # 3.0 s（4/4）
NBARS = 164
DUR = NBARS * BAR          # 492 s
N = int(round(DUR * SR))
PAD = int(6 * SR)
SWING = 0.58               # 轻摇摆：后半拍落在拍内 58% 处
TARGET_LUFS = -20.0
SEED = 20260926
rng = np.random.default_rng(SEED)


def mf(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def db(x):
    return 10.0 ** (x / 20.0)


def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))


# ---------------------------------------------------------------- 磁带 wow
# 全局时间扭曲：所有音高乐器共用同一条时间轴，整体有极轻的磁带晃动（约 ±2 音分），
# 但彼此之间始终音准一致。
_t = np.arange(N + PAD, dtype=np.float64) / SR
_w = 1.0 + 0.0012 * np.sin(2 * np.pi * 0.31 * _t) + 0.0004 * np.sin(2 * np.pi * 4.7 * _t + 1.3)
TW = np.cumsum(_w) / SR
del _t, _w


def warped(start, L):
    L = min(L, len(TW) - start)
    return TW[start:start + L] - TW[start]


def add(bus, start, y, gl=1.0, gr=None):
    """把单声道 y 以 (gl, gr) 增益叠加到立体声 bus[2, N]。"""
    if gr is None:
        gr = gl
    if start >= N:
        return
    if start < 0:
        y = y[-start:]
        start = 0
    e = min(start + len(y), N)
    seg = y[:e - start]
    bus[0, start:e] += (seg * gl).astype(np.float32)
    bus[1, start:e] += (seg * gr).astype(np.float32)


def pan_gains(p):
    """等功率声像，p ∈ [-1, 1]。"""
    a = (p + 1.0) * np.pi / 4.0
    return np.cos(a), np.sin(a)


# ---------------------------------------------------------------- 音色
def rhodes(start, f, vel, hold):
    """FM 电钢琴（Rhodes 质感）：1:1 载波/调制对 + 14:1 的“音叉”瞬态。"""
    tail = 0.45
    L = int((hold + tail) * SR)
    T = warped(start, L)
    L = len(T)
    t = np.arange(L) / SR
    tau2 = 2.4 * (220.0 / f) ** 0.45
    env = 0.3 * np.exp(-t / 0.22) + 0.7 * np.exp(-t / tau2)
    env *= 1.0 - np.exp(-t / 0.0025)
    off = t > hold
    env[off] *= np.exp(-(t[off] - hold) / 0.09)
    nt = min(L, int(0.012 * SR))
    env[-nt:] *= np.linspace(1.0, 0.0, nt)          # 尾端 12 ms 收口，避免截断咔哒
    ph = 2 * np.pi * f * T
    bright = min(1.0, (300.0 / f) ** 0.5)
    I1 = vel * bright * (0.22 + 1.15 * np.exp(-t / 0.30))
    y = np.sin(ph + I1 * np.sin(ph))
    if 14 * f < 9000:
        I2 = 0.9 * vel * np.exp(-t / 0.02)
        y += 0.12 * vel * np.exp(-t / 0.035) * np.sin(ph + I2 * np.sin(14 * ph))
    return y * env * vel ** 1.4


def bass(start, f, vel, hold):
    """轻柔的指弹电贝斯：加性合成，高次谐波衰减更快 + 很轻的拨弦瞬态。"""
    tail = 0.25
    L = int((hold + tail) * SR)
    T = warped(start, L)
    L = len(T)
    t = np.arange(L) / SR
    amps = [1.0, 0.42, 0.20, 0.10, 0.05, 0.025]
    y = np.zeros(L)
    for n, a in enumerate(amps, start=1):
        if n * f > 2000:
            break
        y += a * np.exp(-t * 0.9 * (n - 1)) * np.sin(2 * np.pi * n * f * T + 0.3 * n)
    env = (1.0 - np.exp(-t / 0.006)) * (0.45 * np.exp(-t / 0.15) + 0.55 * np.exp(-t / 1.6))
    off = t > hold
    env[off] *= np.exp(-(t[off] - hold) / 0.06)
    nt = min(L, int(0.012 * SR))
    env[-nt:] *= np.linspace(1.0, 0.0, nt)
    # 拨弦：极短的低通噪声
    k = min(L, int(0.04 * SR))
    nz = rng.standard_normal(k)
    nz = sig.lfilter([0.08], [1, -0.92], nz)
    y[:k] += 0.35 * nz * np.exp(-np.arange(k) / SR / 0.008)
    return y * env * vel ** 1.3


def make_shaker_bank(n=8):
    sos = sig.butter(2, [2800, 8500], btype="band", fs=SR, output="sos")
    bank = []
    for _ in range(n):
        L = int(0.14 * SR)
        t = np.arange(L) / SR
        nz = sig.sosfilt(sos, rng.standard_normal(L + 2000))[2000:]
        att = 0.007 + 0.005 * rng.random()
        env = np.where(t < att, (t / att) ** 2, np.exp(-(t - att) / 0.034))
        y = nz * env
        bank.append(y / np.max(np.abs(y)))
    return bank


def make_brush_bank(n=6):
    sos = sig.butter(2, [900, 4500], btype="band", fs=SR, output="sos")
    lp = sig.butter(2, 30, fs=SR, output="sos")
    bank = []
    for _ in range(n):
        L = int(0.45 * SR)
        t = np.arange(L) / SR
        nz = sig.sosfilt(sos, rng.standard_normal(L + 2000))[2000:]
        grain = sig.sosfilt(lp, rng.standard_normal(L + 4000))[4000:]
        grain = 1.0 + 0.35 * grain / (np.max(np.abs(grain)) + 1e-9)
        rise = 0.09
        env = np.where(t < rise, np.sin(0.5 * np.pi * t / rise) ** 2, np.exp(-(t - rise) / 0.11))
        y = nz * env * grain
        bank.append(y / np.max(np.abs(y)))
    return bank


# ---------------------------------------------------------------- 和声
# F 大调。无根音的爵士钢琴排列（A/B 型），相邻和弦之间声部级进。
CHORDS = {
    #          贝斯根音   电钢琴排列（MIDI）
    "Fmaj9":  (41, [52, 55, 57, 60]),   # E3 G3 A3 C4  = 7 9 3 5
    "Dm9":    (38, [53, 57, 60, 64]),   # F3 A3 C4 E4  = 3 5 7 9
    "Gm9":    (43, [53, 57, 58, 62]),   # F3 A3 Bb3 D4 = 7 9 3 5
    "C13":    (36, [52, 57, 58, 62]),   # E3 A3 Bb3 D4 = 3 13 7 9
    "Bbmaj9": (34, [53, 57, 60, 62]),   # F3 A3 C4 D4  = 5 7 9 3
    "Am7":    (33, [55, 57, 60, 64]),   # G3 A3 C4 E4  = 7 1 3 5
}
PROG_A = ["Fmaj9", "Dm9", "Gm9", "C13"] * 2                                  # Imaj9–vi9–ii9–V13
PROG_B = ["Bbmaj9", "Am7", "Dm9", "C13", "Bbmaj9", "Am7", "Gm9", "C13"]      # IVmaj9–iii7–vi9–V13
SEQ = PROG_A + PROG_B                                                       # 16 小节 = 48 s 一轮


def chord_at(b):
    if b == NBARS - 1:
        return "Fmaj9"
    if b == NBARS - 2:
        return "C13"
    return SEQ[b % len(SEQ)]


def bar_t(b, beat):
    return b * BAR + beat * BEAT


# 电钢琴伴奏型：(拍位, 时值[拍], 力度)
KEY_PATTERNS = [
    ([(0.0, 3.6, 0.95)], 0.30, "block"),
    ([(0.0, 2.2, 0.95), (2 + SWING, 1.25, 0.66)], 0.30, "block"),
    ([(0.0, 1.3, 0.92), (1 + SWING, 2.0, 0.70)], 0.25, "block"),
    ([(0.0, 3.6, 0.88)], 0.15, "roll"),
]
BASS_PATTERNS = [
    ([(0.0, 1.85, 1.00, "R"), (2.0, 1.30, 0.78, "5"), (3 + SWING, 0.34, 0.52, "app")], 0.40),
    ([(0.0, 2.80, 1.00, "R"), (3.0, 0.45, 0.62, "R"), (3 + SWING, 0.34, 0.50, "app")], 0.35),
    ([(0.0, 3.60, 1.00, "R")], 0.25),
]


def choose(options):
    w = np.array([o[1] for o in options], dtype=float)
    return options[rng.choice(len(options), p=w / w.sum())]


def render_keys():
    bus = np.zeros((2, N), np.float32)
    voice_pan = [-0.28, -0.09, 0.09, 0.28]
    for b in range(NBARS):
        _, notes = CHORDS[chord_at(b)]
        if b == NBARS - 1:
            hits, style = [(0.0, 3.8, 0.85)], "roll"
        else:
            hits, _, style = choose(KEY_PATTERNS)
        for hi, (beat, dur, vel) in enumerate(hits):
            use = list(enumerate(notes))
            if hi > 0 and rng.random() < 0.5:
                use = use[1:]                      # 再次触键时常常省掉最低音
            v0 = vel * (1 + 0.06 * rng.standard_normal())
            t0 = bar_t(b, beat) + 0.006 * rng.standard_normal()
            for k, (vi, m) in enumerate(use):
                roll = k * (0.075 if style == "roll" else 0.004 + 0.010 * rng.random())
                s = int(round((t0 + roll) * SR))
                s = max(s, 0)
                v = float(np.clip(v0 * (1 + 0.05 * rng.standard_normal()) * (0.92 if vi == 0 else 1.0), 0.3, 1.1))
                y = rhodes(s, mf(m), v, dur * BEAT - roll)
                gl, gr = pan_gains(voice_pan[vi])
                add(bus, s, y, gl, gr)
    return bus


def render_bass():
    bus = np.zeros(N, np.float32)
    for b in range(NBARS):
        root, _ = CHORDS[chord_at(b)]
        nroot, _ = CHORDS[chord_at(min(b + 1, NBARS - 1))]
        pat = [(0.0, 3.8, 0.95, "R")] if b == NBARS - 1 else choose(BASS_PATTERNS)[0]
        for beat, dur, vel, kind in pat:
            if kind == "R":
                m = root
            elif kind == "5":
                m = root + 7 if root + 7 <= 47 else root - 5
            else:  # 经过音：下一小节根音的下方半音或上方全音
                m = nroot - 1 if rng.random() < 0.6 else nroot + 2
            t0 = bar_t(b, beat) + 0.005 * rng.standard_normal()
            s = max(int(round(t0 * SR)), 0)
            v = float(np.clip(vel * (1 + 0.05 * rng.standard_normal()), 0.3, 1.1))
            y = bass(s, mf(m), v, dur * BEAT)
            e = min(s + len(y), N)
            bus[s:e] += y[:e - s].astype(np.float32)
    return bus


def render_decor():
    """高音装饰：零星一两个和弦音，高八度，像远处的点缀，不成旋律。"""
    bus = np.zeros((2, N), np.float32)
    for b in range(NBARS - 2):
        if rng.random() > 0.45:
            continue
        _, notes = CHORDS[chord_at(b)]
        cand = sorted({n + 12 for n in notes} | {n + 24 for n in notes})
        cand = [c for c in cand if 67 <= c <= 81]
        i = int(rng.integers(len(cand) // 2, len(cand)))
        beat = float(rng.choice([1 + SWING, 2.0, 2 + SWING, 3.0]))
        count = 1 if rng.random() < 0.6 else 2
        for j in range(count):
            m = cand[max(i - j, 0)]
            t0 = bar_t(b, beat + j * SWING) + 0.006 * rng.standard_normal()
            s = int(round(t0 * SR))
            v = 0.55 * (1 + 0.06 * rng.standard_normal()) * (0.85 if j else 1.0)
            y = rhodes(s, mf(m), v, 1.3 * BEAT)
            gl, gr = pan_gains(0.35 if (b % 2 == 0) else -0.2)
            add(bus, s, y, gl, gr)
    return bus


def render_perc():
    bus = np.zeros((2, N), np.float32)
    shaker = make_shaker_bank()
    brush = make_brush_bank()
    sh_acc = [0.50, 0.85, 0.55, 0.90, 0.50, 0.85, 0.55, 0.90]
    sgl, sgr = pan_gains(0.15)
    bgl, bgr = pan_gains(-0.15)
    for b in range(NBARS):
        for k in range(8):
            beat = k // 2 + (SWING if k % 2 else 0.0)
            t0 = bar_t(b, beat) + 0.004 * rng.standard_normal()
            g = sh_acc[k] * (1 + 0.12 * rng.standard_normal())
            y = shaker[int(rng.integers(len(shaker)))] * g
            add(bus, int(round(t0 * SR)), y, sgl, sgr)
        for beat in (1.0, 3.0):
            t0 = bar_t(b, beat) - 0.09 + 0.006 * rng.standard_normal()
            g = 0.55 * (1 + 0.1 * rng.standard_normal())
            y = brush[int(rng.integers(len(brush)))] * g
            add(bus, int(round(t0 * SR)), y, bgl, bgr)
    return bus


# ---------------------------------------------------------------- 编排自动化
def automation(points):
    """points: [(秒, 值)]，相邻点之间用 smoothstep 平滑过渡。"""
    out = np.empty(N, np.float32)
    for (t0, v0), (t1, v1) in zip(points[:-1], points[1:]):
        s0, s1 = int(t0 * SR), min(int(t1 * SR), N)
        if s1 <= s0:
            continue
        x = np.linspace(0.0, 1.0, s1 - s0, endpoint=False)
        out[s0:s1] = v0 + (v1 - v0) * x * x * (3 - 2 * x)
    last = int(points[-1][0] * SR)
    if last < N:
        out[last:] = points[-1][1]
    return out


# 节奏：开头 8 小节没有 → 渐入；中段 234–294 s 退到 20%（“呼吸段”）；结尾渐出
PERC_AUTO = [(0, 0), (9, 0), (27, 1), (234, 1), (246, 0.2), (282, 0.2), (294, 1),
             (456, 1), (474, 0), (DUR, 0)]
# 高音装饰：141–237 s 与 399–465 s 两段，淡入淡出各 12 s
DECOR_AUTO = [(0, 0), (141, 0), (153, 1), (225, 1), (237, 0), (399, 0), (411, 0.85),
              (453, 0.85), (465, 0), (DUR, 0)]


# ---------------------------------------------------------------- 效果
def make_ir(seconds=2.2, rt60=1.7, predelay=0.018):
    L = int(seconds * SR)
    t = np.arange(L) / SR
    env = np.exp(-6.91 * t / rt60)
    irs = []
    for ch in range(2):
        nz = rng.standard_normal(L)
        # 越往后越暗：两段低通噪声按时间交叉
        bright = sig.sosfilt(sig.butter(2, 5000, fs=SR, output="sos"), nz)
        dark = sig.sosfilt(sig.butter(2, 1800, fs=SR, output="sos"), nz)
        x = np.clip(t / 0.8, 0, 1)
        ir = (bright * (1 - x) + dark * x * 1.6) * env
        ir *= np.clip(t / 0.03, 0, 1)                 # 柔和起音
        ir = np.concatenate([np.zeros(int(predelay * SR)), ir])
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    return irs


def peaking(f0, gain_db, q):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    alpha = np.sin(w0) / (2 * q)
    b = np.array([1 + alpha * A, -2 * np.cos(w0), 1 - alpha * A])
    a = np.array([1 + alpha / A, -2 * np.cos(w0), 1 - alpha / A])
    return b / a[0], a / a[0]


def fade(x, fin, fout):
    n_in, n_out = int(fin * SR), int(fout * SR)
    x[..., :n_in] *= (0.5 - 0.5 * np.cos(np.pi * np.arange(n_in) / n_in)).astype(np.float32)
    x[..., -n_out:] *= (0.5 + 0.5 * np.cos(np.pi * np.arange(n_out) / n_out)).astype(np.float32)
    return x


# ---------------------------------------------------------------- 测量 / 写文件
def to_int16(x, dither=True):
    x = np.asarray(x, np.float64)
    if x.ndim == 1:
        x = np.stack([x, x])
    if dither:
        d = (rng.random(x.shape) - rng.random(x.shape))  # TPDF ±1 LSB
        y = np.round(x * 32767.0 + d)
    else:
        y = np.round(x * 32767.0)
    return np.clip(y, -32768, 32767).astype(np.int16).T


def ebur128(path):
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    def grab(key):
        m = re.search(key + r":\s+(-?[\d.]+|-inf)", txt)
        return float(m.group(1)) if m and m.group(1) != "-inf" else float("-inf")
    return {"I": grab("I"), "LRA": grab("LRA"), "TP": grab("Peak")}


def main():
    print("render keys ...", flush=True)
    keys = render_keys()
    print("render bass ...", flush=True)
    bs = render_bass()
    print("render decor ...", flush=True)
    dec = render_decor()
    print("render perc ...", flush=True)
    perc = render_perc()

    # ---- 分轨处理
    keys = sig.sosfilt(sig.butter(2, 110, "high", fs=SR, output="sos"), keys, axis=-1).astype(np.float32)
    keys = sig.sosfilt(sig.butter(2, 3800, fs=SR, output="sos"), keys, axis=-1).astype(np.float32)
    # 电钢琴立体声颤音（Suitcase 式 auto-pan，2.8 Hz，很浅；左右和恒定，单声道兼容）
    tt = np.arange(N, dtype=np.float32) / SR
    trem = (0.12 * np.sin(2 * np.pi * 2.8 * tt)).astype(np.float32)
    keys[0] *= 1 - trem
    keys[1] *= 1 + trem
    del tt, trem

    bs = sig.sosfilt(sig.butter(2, 35, "high", fs=SR, output="sos"), bs).astype(np.float32)
    bs = sig.sosfilt(sig.butter(2, 750, fs=SR, output="sos"), bs).astype(np.float32)
    dec = sig.sosfilt(sig.butter(2, 5000, fs=SR, output="sos"), dec, axis=-1).astype(np.float32)

    # ---- 电平平衡（相对电钢琴 RMS）
    k_rms = rms(keys)
    bs *= np.float32(k_rms * db(-7.0) / rms(bs))
    perc *= np.float32(k_rms * db(-24.0) / rms(perc))
    dec *= np.float32(0.55 * 1.0)   # 装饰单音约为一个伴奏声部的一半
    perc *= automation(PERC_AUTO)
    dec *= automation(DECOR_AUTO)

    # ---- 混响（卷积，合成 IR，RT60≈1.7 s）
    print("reverb ...", flush=True)
    send = (0.5 * (keys[0] + keys[1]) * 0.30 + 0.5 * (dec[0] + dec[1]) * 0.45
            + 0.5 * (perc[0] + perc[1]) * 0.18).astype(np.float32)
    irs = make_ir()
    wet = np.stack([sig.oaconvolve(send, ir.astype(np.float32))[:N] for ir in irs]).astype(np.float32)
    del send

    mix = keys + dec + perc + wet
    mix[0] += bs
    mix[1] += bs
    del keys, dec, perc, wet, bs

    # ---- 母带：去直流/次低频、给人声让位、温暖低通、轻磁带饱和、淡入淡出
    print("master ...", flush=True)
    mix = sig.sosfilt(sig.butter(2, 30, "high", fs=SR, output="sos"), mix, axis=-1)
    b, a = peaking(2500, -2.5, 0.8)
    mix = sig.lfilter(b, a, mix, axis=-1)
    mix = sig.sosfilt(sig.butter(2, 7000, fs=SR, output="sos"), mix, axis=-1)
    rl, rr = rms(mix[0]), rms(mix[1])                  # 左右声道 RMS 对齐（声像居中）
    mix[0] *= np.sqrt(rl * rr) / rl
    mix[1] *= np.sqrt(rl * rr) / rr
    mix = mix / np.max(np.abs(mix)) * 0.7
    mix = np.tanh(1.5 * mix) / 1.5
    mix = sig.sosfilt(sig.butter(1, 25, "high", fs=SR, output="sos"), mix, axis=-1)   # 饱和后再去一次直流
    mix = mix.astype(np.float32)
    mix = fade(mix, 2.0, 3.0)

    # ---- 响度归一到 -20 LUFS（ffmpeg ebur128 测量）
    tmp = os.path.join(TMP, "_bgm_measure.wav")
    wavfile.write(tmp, SR, np.ascontiguousarray(mix.T))
    m0 = ebur128(tmp)
    gain = db(TARGET_LUFS - m0["I"])
    mix *= np.float32(gain)
    peak = float(np.max(np.abs(mix)))
    print(f"pre-norm I={m0['I']} LUFS, gain={20*np.log10(gain):+.2f} dB, sample peak={20*np.log10(peak):.2f} dBFS")
    assert peak < db(-1.0), "峰值过高"
    os.remove(tmp)

    wavfile.write(os.path.join(OUT, "bgm.wav"), SR, to_int16(mix))
    m1 = ebur128(os.path.join(OUT, "bgm.wav"))
    print("bgm.wav:", json.dumps(m1))

    # ---------------------------------------------------------------- SFX
    # 卡片“嗒”：短促的木质轻敲（下滑正弦 + 极短低通噪声），0.12 s
    L = int(0.12 * SR)
    t = np.arange(L) / SR
    f = 470 + 650 * np.exp(-t / 0.012)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.022) * (1 - np.exp(-t / 0.0008))
    body += 0.12 * np.sin(2.3 * ph) * np.exp(-t / 0.008)
    nz = sig.sosfilt(sig.butter(2, 2500, fs=SR, output="sos"), rng.standard_normal(L))
    body += 0.6 * nz / np.max(np.abs(nz)) * np.exp(-t / 0.003) * (1 - np.exp(-t / 0.0005))
    body = sig.sosfilt(sig.butter(2, 5000, fs=SR, output="sos"), body)
    body = sig.sosfilt(sig.butter(2, 120, "high", fs=SR, output="sos"), body)
    body[-int(0.02 * SR):] *= np.linspace(1, 0, int(0.02 * SR))
    pop = body / np.max(np.abs(body)) * db(-6.0)
    wavfile.write(os.path.join(OUT, "sfx_pop.wav"), SR, to_int16(pop))

    # 打勾：两个柔和的马林巴式音 A5 → E6（纯五度上行），0.26 s
    L = int(0.26 * SR)
    t = np.arange(L) / SR
    tick = np.zeros(L)
    for f0, t0, g in ((880.0, 0.0, 0.8), (1318.5, 0.065, 1.0)):
        s = int(t0 * SR)
        tt = t[:L - s]
        env = (1 - np.exp(-tt / 0.0015)) * np.exp(-tt / 0.06)
        v = np.sin(2 * np.pi * f0 * tt) + 0.22 * np.sin(2 * np.pi * 3.93 * f0 * tt) * np.exp(-tt / 0.012)
        tick[s:] += g * v * env
    tick = sig.sosfilt(sig.butter(2, 6000, fs=SR, output="sos"), tick)
    tick[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    tick = tick / np.max(np.abs(tick)) * db(-6.0)
    wavfile.write(os.path.join(OUT, "sfx_tick.wav"), SR, to_int16(tick))
    print("done")


if __name__ == "__main__":
    main()
