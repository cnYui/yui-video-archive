# -*- coding: utf-8 -*-
"""程序合成三首短视频用 BGM（numpy / scipy，没有用任何采样或外部素材，所以没有版权问题；随机种子固定，重跑结果相同）。
和系列 BGM（AI科普/素材/音频/synth_audio.py，80 BPM 的 lo-fi 轻爵士）同一种做法，但是为 45 秒的短视频写的：节奏更明确、开头就有钩子、结尾收得住。

  python make_bgm.py            出 bgm_A_科技脉冲.wav、bgm_B_柔光环境.wav、bgm_C_轻快电子.wav（48 kHz 立体声，约 50 s，−20 LUFS，和系列 BGM 同一个电平）+ 频谱图
  python make_bgm.py A          只出一首

A 科技脉冲  104 BPM · A 小调   冷、略带悬疑：16 分音符的拨弦琶音 + 低频铺底 + 轻脉冲，开头一记低频冲击和下行扫频当钩子（贴“她是 AI”的悬念）
B 柔光环境  88 BPM · D 小调    电影感环境音：慢起音的暖色铺底 + 玻璃铃音小旋律 + 很轻的“心跳”，最安静、最不抢人声
C 轻快电子  112 BPM · C 大调   积极、有推进感：反拍和弦拨弦 + 八分音符低音 + 轻的四四拍底鼓、拍手，一首“科技新闻”的标准底子
三首都给人声让了位置：1–3 kHz 压低 3 dB，铺底 / 低音跟着底鼓轻轻“呼吸”，琶音和旋律放在 500 Hz 以上、音量偏低。
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000
HERE = Path(__file__).resolve().parent
DUR = 50.0                                   # 比成片（45.5 s）长一点，后面混音时会在片尾淡出
TARGET_LUFS = -20.0                          # 和系列 BGM 同一个电平（mix_audio.py 再按 BGM_BED 压到人声下面）


# ───────────────────────── 基础：音高、混入、乐器
def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tarr(n):
    return np.arange(n) / SR


def put(buf, x, start, gain=1.0, pan=0.0):
    """把单声道 x 混进立体声 buf（N×2）的 start 秒处；pan −1 左 … +1 右（等功率）。"""
    i = int(round(start * SR))
    if i >= len(buf) or i < 0:
        return
    x = x[: len(buf) - i]
    th = (pan + 1) * np.pi / 4
    buf[i:i + len(x), 0] += x * gain * np.cos(th)
    buf[i:i + len(x), 1] += x * gain * np.sin(th)


def put_st(buf, xl, xr, start, gain=1.0):
    i = int(round(start * SR))
    if i >= len(buf) or i < 0:
        return
    m = min(len(xl), len(buf) - i)
    buf[i:i + m, 0] += xl[:m] * gain
    buf[i:i + m, 1] += xr[:m] * gain


def pluck(rng, f, dur=0.45, decay=0.2, bright=1.0, nh=14, detune=7.0, vel=1.0):
    """拨弦：两个略失谐的“锯齿”（谐波 1/h 振幅），高次谐波衰减得更快 = 声音随时间变暗；4 ms 起音、尾部 20 ms 淡出。"""
    n = int(dur * SR)
    t = tarr(n)
    out = np.zeros(n)
    for cents in (-detune, detune):
        ff = f * 2 ** (cents / 1200)
        for h in range(1, nh + 1):
            fh = ff * h
            if fh > 14000:
                break
            tau = decay / (1 + 0.55 * (h - 1) * bright)
            out += (1.0 / h ** 1.1) * np.exp(-t / tau) * np.sin(2 * np.pi * fh * t + rng.uniform(0, 2 * np.pi))
    out *= np.minimum(1, t / 0.004) * np.clip((dur - t) / 0.02, 0, 1)
    return vel * out / (np.abs(out).max() + 1e-9)


def bell(rng, f, dur=2.2, ratio=3.5, index=3.0, dec=1.1, vel=1.0):
    """玻璃铃音：FM（载波 : 调制 = 1 : 3.5，调制深度随时间衰减），音色干净、略带金属感。"""
    n = int(dur * SR)
    t = tarr(n)
    idx = index * np.exp(-t / (dec * 0.6))
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t)) * np.exp(-t / dec)
    x += 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / (dec * 0.5))
    x *= np.minimum(1, t / 0.003) * np.clip((dur - t) / 0.05, 0, 1)
    return vel * x / (np.abs(x).max() + 1e-9)


def lead(rng, f, dur=0.5, vel=1.0, vib=5.5, vib_cents=7.0):
    """三角波味的领奏（奇次谐波 1/h²），带一点点颤音。"""
    n = int(dur * SR)
    t = tarr(n)
    vibr = 1 + (2 ** (vib_cents * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / 0.15) / 1200) - 1)
    ph = 2 * np.pi * np.cumsum(f * vibr) / SR
    x = np.zeros(n)
    for h in range(1, 12, 2):
        x += np.sin(h * ph) / h ** 2 * (1 if (h // 2) % 2 == 0 else -1)
    env = np.minimum(1, t / 0.01) * np.exp(-t / (dur * 0.9)) * np.clip((dur - t) / 0.06, 0, 1)
    x *= env
    return vel * x / (np.abs(x).max() + 1e-9)


def pad(rng, freqs, dur, attack=0.8, release=1.2, bright=0.5, nh=10, lfo=0.1):
    """铺底：每个音 2 个失谐声部（左 / 右各偏一点，出宽度）× 谐波（越暗衰减越快），慢起音、慢尾音，轻微的幅度起伏。返回 (左, 右)。"""
    n = int((dur + release) * SR)
    t = tarr(n)
    L = np.zeros(n)
    R = np.zeros(n)
    for f in freqs:
        for cents, wl, wr in ((-8, 1.0, 0.4), (8, 0.4, 1.0)):
            ff = f * 2 ** (cents / 1200)
            for h in range(1, nh + 1):
                fh = ff * h
                if fh > 9000:
                    break
                a = 1.0 / h ** (1.2 + 1.3 * (1 - bright))
                s = np.sin(2 * np.pi * fh * t + rng.uniform(0, 2 * np.pi))
                L += wl * a * s
                R += wr * a * s
    a_env = np.clip(t / attack, 0, 1)
    a_env = a_env * a_env * (3 - 2 * a_env)
    r_env = np.clip((dur + release - t) / release, 0, 1)
    r_env = r_env * r_env * (3 - 2 * r_env)
    mod = 1 + 0.10 * np.sin(2 * np.pi * lfo * t + rng.uniform(0, 6.28))
    env = a_env * r_env * mod
    pk = max(np.abs(L * env).max(), np.abs(R * env).max()) + 1e-9
    return L * env / pk, R * env / pk


def sub(f, dur, vel=1.0, attack=0.02, release=0.15, sat=1.7):
    """低音：正弦 + 一点点二次谐波，轻度饱和（手机喇叭放不出 50 Hz，靠 2 次、3 次谐波听到）。"""
    n = int((dur + release) * SR)
    t = tarr(n)
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    x = np.tanh(sat * x) / np.tanh(sat)
    env = np.minimum(1, t / attack) * np.clip((dur + release - t) / release, 0, 1)
    return vel * x * env


def bass_pluck(rng, f, dur=0.28, vel=1.0):
    """C 用的拨弦低音：锯齿的低通感（高次谐波快速衰减）+ 一点 sub。"""
    n = int(dur * SR)
    t = tarr(n)
    x = np.zeros(n)
    for h in range(1, 9):
        x += (1.0 / h) * np.exp(-t / (0.16 / (1 + 0.9 * (h - 1)))) * np.sin(2 * np.pi * f * h * t)
    x += 0.7 * np.sin(2 * np.pi * f * t)
    x = np.tanh(1.3 * x)
    x *= np.minimum(1, t / 0.004) * np.clip((dur - t) / 0.03, 0, 1)
    return vel * x / (np.abs(x).max() + 1e-9)


def kick(rng, vel=1.0, f0=135, f1=46, dec=0.17):
    n = int(0.5 * SR)
    t = tarr(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.032)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec)
    x += 0.2 * rng.standard_normal(n) * np.exp(-t / 0.004)
    return vel * x


def hat(rng, vel=1.0, open_=False):
    n = int((0.22 if open_ else 0.07) * SR)
    t = tarr(n)
    b, a = signal.butter(2, 7500 / (SR / 2), "high")
    x = signal.lfilter(b, a, rng.standard_normal(n)) * np.exp(-t / (0.09 if open_ else 0.022))
    return vel * x / (np.abs(x).max() + 1e-9)


def clap(rng, vel=1.0):
    n = int(0.3 * SR)
    t = tarr(n)
    b, a = signal.butter(2, [900 / (SR / 2), 3400 / (SR / 2)], "band")
    x = signal.lfilter(b, a, rng.standard_normal(n))
    env = 0.5 * np.exp(-t / 0.11)
    for k, d in enumerate((0, 0.011, 0.023)):
        i = int(d * SR)
        env[i:] += np.exp(-t[: n - i] / 0.009) * (0.6 if k < 2 else 1.0)
    x = x * env
    return vel * x / (np.abs(x).max() + 1e-9)


def boom(vel=1.0, f=52, dec=0.9):
    """低频冲击（电影里的 hit）：从 90 Hz 掉到 52 Hz 的正弦，带 2 次谐波。"""
    n = int(2.2 * SR)
    t = tarr(n)
    ft = f + 45 * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(ft) / SR
    x = np.sin(ph) * np.exp(-t / dec) + 0.3 * np.sin(2 * ph) * np.exp(-t / (dec * 0.45))
    x *= np.minimum(1, t / 0.002)
    return vel * x


def riser(rng, dur, f0=250, f1=9000, down=False):
    """噪声上扫（渐强）；down=True 反过来就是下行扫频（渐弱）。截止频率上扫用 8 个低通噪声按高斯权重交叉淡化来近似。"""
    n = int(dur * SR)
    t = np.arange(n) / n
    nz = rng.standard_normal(n)
    cuts = np.geomspace(f0, f1, 8)
    out = np.zeros(n)
    for k, c in enumerate(cuts):
        b, a = signal.butter(2, min(c, SR / 2 * 0.9) / (SR / 2), "low")
        w = np.exp(-((t - k / (len(cuts) - 1)) ** 2) / (2 * 0.13 ** 2))
        out += signal.lfilter(b, a, nz) * w
    out *= t ** 2.2
    out /= np.abs(out).max() + 1e-9
    return out[::-1] if down else out


def shimmer(rng, dur, lo=3000, hi=9000, vel=1.0):
    """空气感：带通噪声，慢起慢落，铺在高频，给环境类曲子一点“空间”。"""
    n = int(dur * SR)
    t = tarr(n)
    b, a = signal.butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
    x = signal.lfilter(b, a, rng.standard_normal(n))
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return vel * x * env / (np.abs(x).max() + 1e-9)


# ───────────────────────── 效果
def reverb(x, rt=1.8, pre=0.015, damp=5500, seed=1):
    """卷积混响（指数衰减的噪声做脉冲响应，左右不相关）；返回只含湿信号的 N×2。"""
    r = np.random.default_rng(seed)
    n = int(rt * 1.5 * SR)
    t = tarr(n)
    ir = np.zeros((n, 2))
    for ch in range(2):
        nz = r.standard_normal(n) * np.exp(-t * 6.9 / rt)
        b, a = signal.butter(1, damp / (SR / 2), "low")
        nz = signal.lfilter(b, a, nz)
        d = int(pre * SR)
        ir[:, ch] = np.concatenate([np.zeros(d), nz])[:n]
    ir /= np.sqrt((ir ** 2).sum(0).max())
    out = np.zeros_like(x)
    for ch in range(2):
        out[:, ch] = signal.fftconvolve(x[:, ch], ir[:, ch])[: len(x)]
    return out * 6.0


def echo(x, delay, fb=0.4, taps=5, dark=4500):
    """乒乓回声：每一次反馈左右互换、逐次变暗。返回只含回声的 N×2。"""
    d = int(delay * SR)
    out = np.zeros_like(x)
    b, a = signal.butter(1, dark / (SR / 2), "low")
    cur = x
    for k in range(1, taps + 1):
        cur = signal.lfilter(b, a, cur[:, ::-1], axis=0) * fb
        sh = d * k
        if sh >= len(x):
            break
        out[sh:] += cur[: len(x) - sh] if k == 1 else np.roll(cur, 0, axis=0)[: len(x) - sh]
    return out


def echo_simple(x, delay, fb=0.4, taps=5):
    d = int(delay * SR)
    out = np.zeros_like(x)
    for k in range(1, taps + 1):
        sh = d * k
        if sh >= len(x):
            break
        src = x[:, ::-1] if k % 2 else x
        out[sh:] += (fb ** k) * src[: len(x) - sh]
    return out


def peq(x, f0, gain_db, q=0.9):
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return signal.lfilter(np.array(b) / a[0], np.array(a) / a[0], x, axis=0)


def pump(n, times, depth=0.4, rel=0.2):
    """底鼓“呼吸”：每次底鼓后铺底 / 低音的音量先压下去再回来。"""
    g = np.ones(n)
    for ts in times:
        i = int(ts * SR)
        m = min(n - i, int(rel * 5 * SR))
        if m <= 0:
            continue
        g[i:i + m] *= 1 - depth * np.exp(-np.arange(m) / SR / rel)
    return g[:, None]


def lufs_of(a):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                       input=a.astype(np.float32).tobytes(), capture_output=True)
    err = p.stderr.decode("utf-8", "replace")
    import re
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def master(x, fade_in=0.01, fade_out=3.0):
    """母带：高通 35 Hz、低通 15 kHz、1–3 kHz 压 3 dB（给人声让位）、软限幅、响度拉到 −20 LUFS。"""
    b, a = signal.butter(2, 35 / (SR / 2), "high")
    x = signal.lfilter(b, a, x, axis=0)
    b, a = signal.butter(2, 15000 / (SR / 2), "low")
    x = signal.lfilter(b, a, x, axis=0)
    x = peq(x, 2000, -3.0, 0.7)
    x = x / (np.abs(x).max() + 1e-9) * 0.7
    x = np.tanh(1.2 * x) / np.tanh(1.2)
    n = len(x)
    x[: int(fade_in * SR)] *= np.linspace(0, 1, int(fade_in * SR))[:, None]
    x[-int(fade_out * SR):] *= np.linspace(1, 0, int(fade_out * SR))[:, None]
    g = 10 ** ((TARGET_LUFS - lufs_of(x)) / 20)
    x = x * g
    pk = np.abs(x).max()
    if pk > 0.89:                                  # 真峰值留 1 dB 余量
        x = x * (0.89 / pk)
        x = x * 10 ** ((TARGET_LUFS - lufs_of(x)) / 20) if False else x
    return x


def write_wav(path, x):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


# ───────────────────────── 三首曲子
def track_A():
    """A 科技脉冲：104 BPM · A 小调（Am – F – C – G，一小节一个和弦）。"""
    rng = np.random.default_rng(20261004)
    bpm = 104
    beat = 60 / bpm
    bar = 4 * beat
    N = int(DUR * SR)
    nb = int(DUR / bar) + 1
    pads, bas, arp, drm, fx = (np.zeros((N, 2)) for _ in range(5))
    chords = [[57, 60, 64], [57, 60, 65], [55, 60, 64], [55, 59, 62]]
    roots = [45, 41, 48, 43]
    pattern = [0, 2, 3, 2, 1, 3, 4, 3, 2, 4, 5, 4, 3, 5, 4, 2]
    accent = [1.0, 0.45, 0.7, 0.45, 0.85, 0.45, 0.7, 0.45, 0.95, 0.45, 0.7, 0.45, 0.85, 0.45, 0.7, 0.5]
    kick_t = []
    for b in range(nb):
        t0 = b * bar
        ch = chords[b % 4]
        L, R = pad(rng, [hz(m) for m in ch], bar, attack=0.7, release=1.0, bright=0.45)
        put_st(pads, L, R, t0, 0.32)
        put(bas, sub(hz(roots[b % 4]), bar * 0.96), t0, 0.5 if b >= 2 else 0.4)
        full = (4 <= b < 12) or (16 <= b < 20)
        half = (12 <= b < 16) or b >= 20
        sparse = 2 <= b < 4
        notes = [hz(c + 12) for c in ch] + [hz(c + 24) for c in ch]
        for s in range(16):
            if full or (half and s % 2 == 0) or (sparse and s % 4 == 0):
                v = accent[s] * (0.9 if full else 0.7)
                put(arp, pluck(rng, notes[pattern[s]], 0.42, 0.18, 1.0, vel=v), t0 + s * beat / 4, 0.5, pan=(-0.35 if s % 2 else 0.35))
        if full or sparse:
            for k in range(4):
                tk = t0 + k * beat
                put(drm, kick(rng, 0.9 if full else 0.5), tk, 0.55)
                kick_t.append(tk)
        if full:
            for k in range(4):
                put(drm, hat(rng, 0.5), t0 + k * beat + beat / 2, 0.16, pan=0.25)
            if b >= 8:
                for s in range(16):
                    if s % 2 == 1:
                        put(drm, hat(rng, 0.25), t0 + s * beat / 4, 0.1, pan=-0.2)
    # 钩子：开头的低频冲击 + 下行扫频；两个段落转换处各一个上扫 + 冲击
    put(fx, boom(1.0), 0.0, 0.5)
    put(fx, riser(rng, 1.6, 400, 9000, down=True), 0.0, 0.16)
    for tb in (4, 16):
        put(fx, riser(rng, bar * 1.5), (tb - 1.5) * bar, 0.2)
        put(fx, boom(0.8), tb * bar, 0.4)
    # 铺底 / 低音跟着底鼓“呼吸”
    g = pump(N, kick_t, 0.35, 0.2)
    pads *= g
    bas *= g
    # 效果：铺底长混响，琶音回声 + 短混响
    arp_echo = echo_simple(arp, beat * 0.75, 0.45, 5)
    mix = (pads + 0.4 * reverb(pads, 2.4, seed=2) + bas + arp + 0.55 * arp_echo + 0.25 * reverb(arp + arp_echo, 1.3, seed=3) + drm + fx)
    return master(mix)


def track_B():
    """B 柔光环境：88 BPM · D 小调（Dm – Bb – F – C）。"""
    rng = np.random.default_rng(20261005)
    bpm = 88
    beat = 60 / bpm
    bar = 4 * beat
    N = int(DUR * SR)
    nb = int(DUR / bar) + 1
    pads, bas, mel, drm, fx = (np.zeros((N, 2)) for _ in range(5))
    chords = [[50, 57, 62, 65], [46, 53, 58, 62], [53, 57, 60, 65], [48, 55, 60, 64]]
    roots = [38, 34, 41, 36]
    # 铃音小旋律（4 小节一轮）：(拍位置, MIDI)
    motif = [[(1.0, 81), (2.5, 77)], [(1.0, 74), (2.5, 77)], [(1.0, 84), (2.0, 81), (3.0, 77)], [(1.0, 79), (2.5, 76)]]
    kick_t = []
    for b in range(nb):
        t0 = b * bar
        L, R = pad(rng, [hz(m) for m in chords[b % 4]], bar, attack=1.2, release=1.6, bright=0.35, nh=8, lfo=0.08)
        put_st(pads, L, R, t0, 0.5)
        put(bas, sub(hz(roots[b % 4]), bar * 0.98, attack=0.15, release=0.4), t0, 0.5)
        if b >= 2:
            for pos, m in motif[b % 4]:
                put(mel, bell(rng, hz(m), 2.6, vel=0.8 if b % 8 < 4 else 0.65), t0 + pos * beat, 0.34, pan=-0.3 if pos < 2 else 0.3)
        if b >= 2 and not (12 <= b < 14):
            for tk in (t0, t0 + 2.5 * beat):
                put(drm, kick(rng, 0.45 if tk == t0 else 0.25, 100, 42, 0.22), tk, 0.5)
                kick_t.append(tk)
        if b >= 4:
            put(fx, shimmer(rng, bar * 0.9, 3000, 9000, 1.0), t0 + 0.05, 0.05 if b < 16 else 0.07)
            for k in (1, 3):
                put(drm, hat(rng, 0.35), t0 + (k + 0.5) * beat, 0.1, pan=0.3)
    put(fx, boom(0.7, 46, 1.2), 0.0, 0.4)
    put(fx, riser(rng, bar * 2, 300, 7000, down=True), 0.0, 0.1)
    put(fx, riser(rng, bar * 2), 14 * bar, 0.16)
    put(fx, boom(0.6, 46, 1.2), 16 * bar, 0.35)
    g = pump(N, kick_t, 0.2, 0.3)
    pads *= g
    mel_echo = echo_simple(mel, beat * 0.75, 0.5, 5)
    mix = pads + 0.5 * reverb(pads, 3.2, seed=5) + bas + mel + 0.6 * mel_echo + 0.5 * reverb(mel + mel_echo, 2.4, seed=6) + drm + fx
    return master(mix)


def track_C():
    """C 轻快电子：112 BPM · C 大调（C – G – Am – F）。"""
    rng = np.random.default_rng(20261006)
    bpm = 112
    beat = 60 / bpm
    bar = 4 * beat
    N = int(DUR * SR)
    nb = int(DUR / bar) + 1
    pads, bas, stab, drm, ld, fx = (np.zeros((N, 2)) for _ in range(6))
    chords = [[60, 64, 67], [59, 62, 67], [60, 64, 69], [60, 65, 69]]
    roots = [36, 43, 45, 41]
    bass_steps = [(0, 0, 1.0), (2, 0, 0.7), (4, 0, 1.0), (5, 12, 0.7), (7, 7, 0.8)]
    lead_motif = [[(0, 76), (1, 79), (2, 81), (3, 79)], [(0, 79), (1, 83), (2, 81), (3, 79)], [(0, 76), (1, 81), (2, 84), (3, 81)], [(0, 77), (1, 81), (2, 79), (3, 77)]]
    kick_t = []
    for b in range(nb):
        t0 = b * bar
        ch = chords[b % 4]
        full = (4 <= b < 12) or (16 <= b < 20)
        brk = 12 <= b < 16
        out = b >= 20
        L, R = pad(rng, [hz(m - 12) for m in ch], bar, attack=0.3, release=0.6, bright=0.55, nh=8)
        put_st(pads, L, R, t0, 0.28)
        if not brk:
            for st, off, v in bass_steps:
                put(bas, bass_pluck(rng, hz(roots[b % 4] + off), 0.26, v), t0 + st * beat / 2, 0.5)
            for k in range(4):
                tk = t0 + k * beat
                put(drm, kick(rng, 0.8 if not out else 0.5), tk, 0.5)
                kick_t.append(tk)
        for k in range(4):                                       # 反拍和弦拨弦
            if not brk or k % 2 == 1:
                for j, m in enumerate(ch):
                    put(stab, pluck(rng, hz(m + 12), 0.22, 0.11, 1.2, nh=10, vel=0.9 if k % 2 == 0 else 0.7), t0 + (k + 0.5) * beat + j * 0.004, 0.16, pan=(-0.4, 0.0, 0.4)[j])
        if b >= 2 and not brk and not out:
            for k in (1, 3):
                put(drm, clap(rng, 0.7), t0 + k * beat, 0.3)
        if b >= 2 and not brk:
            for s in range(8):
                put(drm, hat(rng, 0.5 if s % 2 else 0.2), t0 + s * beat / 2, 0.1, pan=0.2)
        if full or brk:
            for pos, m in lead_motif[b % 4]:
                put(ld, lead(rng, hz(m), beat * 0.95, 0.8), t0 + pos * beat, 0.3, pan=0.15)
    put(fx, riser(rng, bar * 1.5, 500, 11000), 14.5 * bar, 0.2)
    put(fx, boom(0.6, 58, 0.6), 16 * bar, 0.35)
    put(fx, riser(rng, 1.2, 600, 10000, down=True), 0.0, 0.12)
    g = pump(N, kick_t, 0.4, 0.17)
    pads *= g
    bas *= g
    stab_echo = echo_simple(stab, beat * 0.75, 0.4, 4)
    ld_echo = echo_simple(ld, beat * 0.75, 0.4, 4)
    mix = pads + 0.3 * reverb(pads, 1.6, seed=7) + bas + stab + 0.5 * stab_echo + ld + 0.5 * ld_echo + 0.25 * reverb(ld + stab, 1.2, seed=8) + drm + fx
    return master(mix)


TRACKS = {"A": ("bgm_A_科技脉冲.wav", track_A), "B": ("bgm_B_柔光环境.wav", track_B), "C": ("bgm_C_轻快电子.wav", track_C)}


def spectrogram_png(x, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    m = x.mean(1)
    f, t, S = signal.spectrogram(m, SR, nperseg=4096, noverlap=3072)
    fig, ax = plt.subplots(2, 1, figsize=(14, 6), gridspec_kw={"height_ratios": [1, 2]})
    ax[0].plot(np.arange(len(m)) / SR, m, lw=0.3)
    ax[0].set_xlim(0, len(m) / SR)
    ax[1].pcolormesh(t, f, 10 * np.log10(S + 1e-12), shading="auto", vmin=-110, vmax=-40)
    ax[1].set_ylim(0, 9000)
    fig.tight_layout()
    fig.savefig(path, dpi=70)
    plt.close(fig)


def main():
    want = [a for a in sys.argv[1:] if a in TRACKS] or list(TRACKS)
    for k in want:
        name, fn = TRACKS[k]
        x = fn()
        write_wav(HERE / name, x)
        spectrogram_png(x, HERE / name.replace(".wav", ".png"))
        print(f"{name}: {len(x) / SR:.1f} s，{lufs_of(x):.1f} LUFS，采样峰值 {20 * np.log10(np.abs(x).max()):.1f} dBFS")


if __name__ == "__main__":
    main()
