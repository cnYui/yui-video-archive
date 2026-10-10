# -*- coding: utf-8 -*-
"""整片混音 → audio/mix.wav（48 kHz 立体声，长度 = 整片帧数 / 30）+ audio/voice_only.wav（只有配音，复核用）。
claude-code-episode 的 mix_audio.py + OpenAI-DevDay 的同传混法。

- 画外音和同传：../02_配音/edit/tts_narration.wav（Fish 网页版「温柔男生」），高通 70 Hz + 两遍法 loudnorm 到 −16 LUFS（线性增益），
  按 TL.tts.blocks = [b0, b1, at, speed] 切块放进去（同传念不完的块带加速，atempo 不变调）。
- 素材原声（HAS_AUDIO 里写 True 的素材）：
  · 同传段（range 的 mode = dub）：高通 90 Hz + 轻压缩 + loudnorm，再压到固定的 −29 LUFS 垫在下面（听得见是谁在说、什么语气；gain_db 可微调），不再随配音起伏；
  · 画外音段（mode = vo）：同一个素材里用到的片段拼起来量一次响度，用同一个线性增益拉到 −21 LUFS，有人说话压 −9 dB；range 里写 "mute": true 就不放这段的原声（讲解盖在访谈画面上时用）。
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav），全程垫在下面（−16 dB），不够长从第 48 s 起循环（交叉淡化 1.5 s），头 1 s 淡入、尾 2 s 淡出；
  同传段里 BGM 压到 ×0.12（前后 0.4 s 渐变），其他有原声的段落 ×0.05；没人说话、素材也没声音的时候抬高 8 dB。
- 整片 −16 LUFS + 软限幅 −1 dBFS。
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
NARR_LUFS, FOOT_LUFS, DUB_LUFS, BGM_BED, BGM_DUCK, DUB_BGM_DUCK, VOICE_DUCK_DB = -16.0, -21.0, -29.0, -16.0, 0.05, 0.12, -9.0
TARGET_LUFS = -16.0
BGM_SWELL_DB = 8.0                 # 没人说话、素材也没声音的时候，BGM 抬高这么多（0.4 s 渐变），不让安静段像“没声音”


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


def stretch(a, speed):
    """f32 立体声数组按倍数加速（atempo，不变调）。"""
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", f"atempo={speed:.4f}",
                        "-f", "f32le", "-ar", str(SR), "-ac", "2", "-"], input=a.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32).reshape(-1, 2).copy()


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


def save_wav(path, mix):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())


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
        speed = blk[3] if len(blk) > 3 else 1.0
        seg = tts[int(round(b0 * SR)): int(round(b1 * SR))]
        if abs(speed - 1.0) > 1e-3:
            seg = stretch(seg, speed)
        k = int(round(off * SR))
        voice[k: k + len(seg)] += seg[: max(0, n - k)]

    bgm_gain = np.ones(n, np.float32)
    ramp = int(0.4 * SR)
    f = int(0.03 * SR)
    info = []

    # 同传段：素材原声压到固定的 DUB_LUFS
    dubfoot = np.zeros((n, 2), np.float32)
    dub_ranges = [(cid, r) for cid, c in T["clips"].items() for r in c["ranges"] if r.get("mode") == "dub" and HAS_AUDIO[r["src"]] and not r["mute"] and not r.get("hold")]
    for cid, r in dub_ranges:
        tgt = DUB_LUFS + r.get("gain_db", 0)
        src = AUDIO_SRC.get(r["src"], SRC[r["src"]])
        dur = r["out"] - r["in"]
        af = f"highpass=f=90,acompressor=threshold=-34dB:ratio=3:attack=8:release=160:makeup=2,loudnorm=I={tgt}:TP=-2.5:LRA=8"
        a = load(src, af=af, ss=r["in"], t=dur)
        cur = lufs_of(load(src, ss=r["in"], t=dur))
        cur_a = lufs_of(a)
        a = a * (10 ** ((tgt - cur_a) / 20))                  # loudnorm 在短片段上偏差大，量一遍补到目标
        if np.abs(a).max() > 0.85:
            a = a * (0.85 / float(np.abs(a).max()))
        a[:f] *= np.linspace(0, 1, f)[:, None]
        a[-f:] *= np.linspace(1, 0, f)[:, None]
        k = int(round(r["s"] * SR))
        dubfoot[k: k + len(a)] += a[: max(0, n - k)]
        k0, k1 = max(0, k - ramp), min(n, k + len(a) + ramp)
        d = np.full(k1 - k0, DUB_BGM_DUCK, np.float32)
        rr = min(ramp, len(d) // 2)
        d[:rr] = np.linspace(1, DUB_BGM_DUCK, rr)
        d[-rr:] = np.linspace(DUB_BGM_DUCK, 1, rr)
        bgm_gain[k0:k1] = np.minimum(bgm_gain[k0:k1], d)
        info.append(f"{cid}({r['in']:.0f}s) 原始 {cur:.1f} → {lufs_of(a):.1f} LUFS")

    # 画外音段的素材原声：同一个素材里用到的片段拼起来量一次响度，用同一个线性增益
    ranges = [(cid, r) for cid, c in T["clips"].items() for r in c["ranges"] if r.get("mode") != "dub" and HAS_AUDIO[r["src"]] and not r["mute"] and not r.get("hold")]
    raw = {}
    for cid, r in ranges:
        raw[(cid, r["s"])] = load(AUDIO_SRC.get(r["src"], SRC[r["src"]]), ss=r["in"], t=r["out"] - r["in"])
    gains = {}
    for key in sorted({r["src"] for _, r in ranges}):
        cat = np.concatenate([raw[(cid, r["s"])] for cid, r in ranges if r["src"] == key])
        cur = lufs_of(cat)
        gains[key] = 10 ** ((FOOT_LUFS - cur) / 20)
        info.append(f"{key}(画外音段) 原始 {cur:.1f} LUFS → {FOOT_LUFS}（增益 {20 * np.log10(gains[key]):+.1f} dB）")
    foot = np.zeros((n, 2), np.float32)
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
        d = np.full(k1 - k0, BGM_DUCK, np.float32)
        rr = min(ramp, len(d) // 2)
        d[:rr] = np.linspace(1, BGM_DUCK, rr)
        d[-rr:] = np.linspace(BGM_DUCK, 1, rr)
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
    mix = voice + dubfoot + foot + bgm
    # 整体拉到 −16 LUFS（频道惯例），峰值超过 −1 dBFS 的少数采样点用软限幅压回去
    cur, pk = lufs_of(mix), float(np.abs(mix).max())
    g = 10 ** ((TARGET_LUFS - cur) / 20)
    mix *= g
    lim = 10 ** (-1.0 / 20)
    over = np.abs(mix) > lim
    mix[over] = np.sign(mix[over]) * (lim + (np.abs(mix[over]) - lim) * 0.2)
    mix = np.clip(mix, -lim, lim)
    save_wav(out_path, mix)
    vo = np.clip(voice * g, -lim, lim)
    save_wav(out_path.parent / "voice_only.wav", vo)                        # 只有配音（和 mix 同一时间轴、同一增益），qa_mix 用它逐句核对
    print(f"mix.wav {n / SR:.2f}s；配音原始 {tts_i} LUFS → {NARR_LUFS}；素材原声 {'；'.join(info) or '无'}；整片 {lufs_of(mix):.1f} LUFS，峰值 {20 * np.log10(float(np.abs(mix).max())):.1f} dBFS")


if __name__ == "__main__":
    main()
