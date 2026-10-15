# -*- coding: utf-8 -*-
"""整片混音 → audio/mix.wav（48 kHz 立体声，长度 = 整片帧数 / 30）。做法照《国内订阅Codex/Claude教程》的 mix_audio.py。

- 画外音：../02_配音/edit/tts_narration.wav（Fish 网页版「赛马娘（曼波欧耶版）」），高通 70 Hz + 两遍法 loudnorm 到 −16 LUFS（线性增益），
  按 TL.tts.blocks = [b0, b1, at] 切块放进去。
- 现场片段（v2）：原声（白宫官方 / PBS）压到 −29 LUFS 垫在同传下面（还听得见是谁在说、什么语气），首尾各 0.04 s 淡入淡出；上面是同一个声音的中文同传，和画外音一样 −16 LUFS；
  片段播放时 BGM 压低（×0.35，前后各 0.3 s 渐变）。
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav），全程垫在下面（−16 dB），不够长从第 48 s 起循环（交叉淡化 1.5 s），头 1 s 淡入、尾 2 s 淡出。
- 最后限幅 −1 dBTP。
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
TTS = HERE.parent / "02_配音" / "edit" / "tts_narration.wav"
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
LIVE = EP / "素材" / "现场视频"
SRC = {"wh": LIVE / "wh_official_6UBA8iL3x54.mp4", "pbs": LIVE / "pbs_1XVhpiRSHv8.mp4", "x": LIVE / "x_user_clip.mp4"}   # x = 用户给的 X 平台竖屏视频
SR, FPS = 48000, 30
NARR_LUFS, CLIP_LUFS, BGM_BED, BGM_DUCK = -16.0, -29.0, -16.0, 0.35


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
    """f32 立体声数组 → 综合响度。"""
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                       input=a.tobytes(), capture_output=True)
    err = p.stderr.decode("utf-8", "replace")
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def gain_to(a, target):
    cur = lufs_of(a)
    return a * (10 ** ((target - cur) / 20)), cur


def normalized(path, target=NARR_LUFS):
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                         f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(p1[p1.rindex("{"): p1.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    return load(path, af), m["input_i"]


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    n = T["frames"] * SR // FPS
    voice = np.zeros((n, 2), np.float32)
    tts, tts_i = normalized(TTS)
    for blk in T["tts"]["blocks"]:
        b0, b1, off = blk[:3]
        speed = blk[3] if len(blk) > 3 else 1.0
        seg = tts[int(round(b0 * SR)): int(round(b1 * SR))]
        if abs(speed - 1.0) > 1e-3:
            seg = stretch(seg, speed)
        k = int(round(off * SR))
        voice[k: k + len(seg)] += seg[: max(0, n - k)]
    duck = np.ones(n, np.float32)
    info = []
    for cid, c in T["clips"].items():
        # 现场原声：PBS 的会后问答是远场收音，原始响度 −37…−40 LUFS，线性拉 20 dB 会削波、底噪也一起抬；
        # 先高通 90 Hz、压一下动态（acompressor），再 loudnorm 单遍（动态）到 −19 LUFS、真峰值 −2.5 dBTP
        tgt = CLIP_LUFS + c.get("gain_db", 0)
        af = (f"highpass=f=90,acompressor=threshold=-34dB:ratio=3:attack=8:release=160:makeup=2,"
              f"loudnorm=I={tgt}:TP=-2.5:LRA=8")
        a = load(SRC[c["src"]], af=af, ss=c["in"], t=c["out"] - c["in"])
        cur = lufs_of(load(SRC[c["src"]], ss=c["in"], t=c["out"] - c["in"]))
        pk = float(np.abs(a).max())
        a, now = gain_to(a, tgt)
        if np.abs(a).max() > 0.85:                       # 拉到目标后峰值超过 −1.4 dBFS 就回退
            a = a * (0.85 / float(np.abs(a).max()))
        f = int(0.04 * SR)
        a[:f] *= np.linspace(0, 1, f)[:, None]
        a[-f:] *= np.linspace(1, 0, f)[:, None]
        k = int(round(c["s"] * SR))
        voice[k: k + len(a)] += a[: max(0, n - k)]
        ramp = int(0.3 * SR)
        k0, k1 = max(0, k - ramp), min(n, k + len(a) + ramp)
        d = np.full(k1 - k0, BGM_DUCK, np.float32)
        r = min(ramp, len(d) // 2)
        d[:r] = np.linspace(1, BGM_DUCK, r)
        d[-r:] = np.linspace(BGM_DUCK, 1, r)
        duck[k0:k1] = np.minimum(duck[k0:k1], d)
        info.append(f"{cid} 原始 {cur:.1f} LUFS → {lufs_of(a):.1f}（峰值 {20*np.log10(max(1e-9, float(np.abs(a).max()))):.1f} dBFS）")
    b = load(BGM)
    xf = int(1.5 * SR)
    out = b.copy()
    loop = b[48 * SR:]
    while len(out) < n + SR:
        ramp = np.linspace(0, 1, xf)[:, None]
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - ramp) + loop[:xf] * ramp, loop[xf:]])
    bgm = out[:n] * (10 ** (BGM_BED / 20)) * duck[:, None]
    bgm[:SR] *= np.linspace(0, 1, SR)[:, None]
    bgm[-2 * SR:] *= np.linspace(1, 0, 2 * SR)[:, None]
    mix = voice + bgm
    lim = 10 ** (-1.0 / 20)
    over = np.abs(mix) > lim
    mix[over] = np.sign(mix[over]) * (lim + (np.abs(mix[over]) - lim) * 0.2)
    mix = np.clip(mix, -lim, lim)
    (HERE / "audio").mkdir(exist_ok=True)
    with wave.open(str(HERE / "audio" / "mix.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(f"mix.wav {n / SR:.2f}s；配音原始 {tts_i} LUFS → {NARR_LUFS}；现场片段 {'，'.join(info)} → {CLIP_LUFS}；整片 {lufs_of(mix):.1f} LUFS")


if __name__ == "__main__":
    main()
