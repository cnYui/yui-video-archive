# -*- coding: utf-8 -*-
"""整片混音 → audio/mix.wav（48 kHz 立体声，长度 = 整片帧数 / 30）。照白宫那条的 mix_audio.py 改：素材是主角，原声要听得见。

- 画外音：../02_配音/edit/tts_narration.wav（Fish 网页版「赛马娘（曼波欧耶版）」），高通 70 Hz + 两遍法 loudnorm 到 −16 LUFS（线性增益），
  按 TL.tts.blocks = [b0, b1, at, speed] 切块放进去。
- 素材原声（g1、m1、p2 有声，k1 是发布会的单独音频；其余无声）：同一个素材里用到的所有片段拼起来量一次响度，用同一个线性增益拉到 −21 LUFS（短片段单独 loudnorm 不稳）；
  每段首尾各 0.03 s 淡入淡出；有人说话时压 −9 dB（0.12 s 起压、0.4 s 放）。range 里写 "mute": true 就不放这段的原声。
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav），全程垫在下面（−16 dB），不够长从第 48 s 起循环（交叉淡化 1.5 s），头 1 s 淡入、尾 2 s 淡出；
  短视频版：有原声的素材段里 BGM 不压（同传短视频每段都有原声，压了就听不见）；素材自带音乐的写进 BGM_DUCK_BY_SRC 再压 −6 dB；没人说话的空档抬 +5 dB。
- 最后限幅 −1 dBTP。
"""
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

from common import AUDIO_SRC, FPS, HAS_AUDIO, HERE, SRC

TTS = HERE.parent / "02_配音" / "edit" / "tts_narration.wav"
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
SR = 48000
NARR_LUFS, FOOT_LUFS, BGM_BED, BGM_DUCK, VOICE_DUCK_DB = -16.0, -21.0, -16.0, 1.0, -9.0
# 短视频：BGM 整条垫底（−16 dB ≈ −36 LUFS，比配音低约 20 dB），**有原声的素材段也不再压**（BGM_DUCK = 1.0）。
# 横屏引擎原来是有原声就压到 ×0.05——同传短视频每段都有原声，BGM 就等于听不见（2026-10-04 第 2 条短视频，用户“加 bgm”后实测改的）。
TARGET_LUFS = -16.0
BGM_DUCK_BY_SRC = {}               # 素材自己带音乐的，BGM 在它的段落里再压一点：写 {"d1": 0.5}（−6 dB）；讲话 / 环境声的素材不用写
BGM_SWELL_DB = 5.0                 # 没人说话的空档（同传之间），BGM 抬高这么多（0.4 s 渐变），不让安静段像“没声音”（第 2 条用 +5 dB）


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True)


def load(path, af=None, ss=None, t=None):
    args = ["ffmpeg", "-v", "error"]
    if ss is not None:
        args += ["-ss", f"{ss:.3f}"]
    args += ["-i", str(path)]
    if t is not None:
        args += ["-t", f"{t:.3f}"]
    args += ["-vn"]
    if af:
        args += ["-af", af]
    args += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(run(args).stdout, dtype=np.float32).reshape(-1, 2).copy()


def lufs_of(a):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                       input=a.astype(np.float32).tobytes(), capture_output=True)
    err = p.stderr.decode("utf-8", "replace")
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def normalized(path, target=NARR_LUFS):
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                         f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(p1[p1.rindex("{"): p1.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    return load(path, af), m["input_i"]


def voice_duck(voice, n):
    """有人说话的地方素材原声压 VOICE_DUCK_DB：10 ms 一格的包络，前 0.12 s、后 0.4 s 保持，再平滑 0.15 s。"""
    hop = SR // 100
    k = n // hop
    m = voice[: k * hop].mean(1)
    rms = 20 * np.log10(np.sqrt((m.reshape(k, hop) ** 2).mean(1)) + 1e-9)
    act = (rms > -50).astype(np.float32)
    pad = np.pad(act, (12, 40))
    dil = np.array([pad[i: i + 53].max() for i in range(k)], np.float32)
    sm = np.convolve(dil, np.ones(15) / 15, mode="same")
    g = 1 - (1 - 10 ** (VOICE_DUCK_DB / 20)) * sm
    x = (np.arange(n) / hop)
    return np.interp(x, np.arange(k), g).astype(np.float32)


def main():
    # 试混用：--tts <wav> 换配音文件，--out <wav> 换输出（默认 ../02_配音/edit/tts_narration.wav → audio/mix.wav）
    arg = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    tts_path, out_path = arg("--tts", TTS), arg("--out", HERE / "audio" / "mix.wav")
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    n = T["frames"] * SR // FPS
    voice = np.zeros((n, 2), np.float32)
    tts, tts_i = normalized(tts_path)
    for blk in T["tts"]["blocks"]:
        b0, b1, off = blk[:3]
        seg = tts[int(round(b0 * SR)): int(round(b1 * SR))]
        k = int(round(off * SR))
        if k < 0:                                   # 第一句从 0 s 开口（短视频没有片头），切点比有声音的起点还早约 0.01 s：把多出来的静音切掉，别让下标变负（Tavus-Griffin 那条撞上过）
            seg, k = seg[-k:], 0
        voice[k: k + len(seg)] += seg[: max(0, n - k)]

    # 素材原声：同一个素材里用到的片段拼起来量一次响度，用同一个线性增益
    ranges = [(cid, r) for cid, c in T["clips"].items() for r in c["ranges"] if HAS_AUDIO[r["src"]] and not r["mute"] and not r.get("hold")]
    raw = {}
    for cid, r in ranges:
        raw[(cid, r["s"])] = load(AUDIO_SRC.get(r["src"], SRC[r["src"]]), ss=r["in"], t=r["out"] - r["in"])
    gains, info = {}, []
    for key in sorted({r["src"] for _, r in ranges}):
        cat = np.concatenate([raw[(cid, r["s"])] for cid, r in ranges if r["src"] == key])
        cur = lufs_of(cat)
        gains[key] = 10 ** ((FOOT_LUFS - cur) / 20)
        info.append(f"{key} 原始 {cur:.1f} LUFS → {FOOT_LUFS}（增益 {20 * np.log10(gains[key]):+.1f} dB）")
    foot = np.zeros((n, 2), np.float32)
    bgm_gain = np.ones(n, np.float32)
    ramp = int(0.4 * SR)
    f = int(0.03 * SR)
    for cid, r in ranges:
        a = raw[(cid, r["s"])] * gains[r["src"]] * (10 ** (r.get("gain_db", 0) / 20))
        if np.abs(a).max() > 0.85:
            a = a * (0.85 / float(np.abs(a).max()))
        if len(a) > 2 * f:
            a[:f] *= np.linspace(0, 1, f)[:, None]
            a[-f:] *= np.linspace(1, 0, f)[:, None]
        k = int(round(r["s"] * SR))
        foot[k: k + len(a)] += a[: max(0, n - k)]
        k0, k1 = max(0, k - ramp), min(n, k + len(a) + ramp)
        bd = BGM_DUCK_BY_SRC.get(r["src"], BGM_DUCK)
        d = np.full(k1 - k0, bd, np.float32)
        rr = min(ramp, len(d) // 2)
        d[:rr] = np.linspace(1, bd, rr)
        d[-rr:] = np.linspace(bd, 1, rr)
        bgm_gain[k0:k1] = np.minimum(bgm_gain[k0:k1], d)
    vd = voice_duck(voice, n)
    foot *= vd[:, None]
    act = (1 - vd) / (1 - 10 ** (VOICE_DUCK_DB / 20))                       # 0 = 没人说话，1 = 正在说话
    swell = 1 + (10 ** (BGM_SWELL_DB / 20) - 1) * (1 - act)                 # 有人说话 ×1，没人说话 ×2.5
    bgm_gain *= np.where(bgm_gain >= 0.99, swell, 1.0).astype(np.float32)   # 素材有原声的段落（bgm_gain 已被压低）不抬

    b = load(BGM)
    xf = int(1.5 * SR)
    out = b.copy()
    loop = b[48 * SR:]
    while len(out) < n + SR:
        rmp = np.linspace(0, 1, xf)[:, None]
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - rmp) + loop[:xf] * rmp, loop[xf:]])
    bgm = out[:n] * (10 ** (BGM_BED / 20)) * bgm_gain[:, None]
    bgm[:SR] *= np.linspace(0, 1, SR)[:, None]
    bgm[-2 * SR:] *= np.linspace(1, 0, 2 * SR)[:, None]
    mix = voice + foot + bgm
    # 整体拉到 −16 LUFS（频道惯例），峰值超过 −1 dBFS 的少数采样点用软限幅压回去
    cur, pk = lufs_of(mix), float(np.abs(mix).max())
    g = 10 ** ((TARGET_LUFS - cur) / 20)               # 按响度目标拉；峰值只有个别几秒超过 −1 dBFS（这期实测 0.0007% 的采样点），下面的软限幅压住
    mix *= g
    lim = 10 ** (-1.0 / 20)
    over = np.abs(mix) > lim
    mix[over] = np.sign(mix[over]) * (lim + (np.abs(mix[over]) - lim) * 0.2)
    mix = np.clip(mix, -lim, lim)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(f"mix.wav {n / SR:.2f}s；配音原始 {tts_i} LUFS → {NARR_LUFS}；素材原声 {'；'.join(info) or '无'}；整片 {lufs_of(mix):.1f} LUFS，峰值 {20 * np.log10(float(np.abs(mix).max())):.1f} dBFS")


if __name__ == "__main__":
    main()
