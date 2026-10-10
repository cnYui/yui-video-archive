# -*- coding: utf-8 -*-
"""整片混音 → out/<ep>/audio/mix.wav（48 kHz 立体声，长度 = 整片帧数 / 30）。做法照《白宫超级智能协定》的 mix_audio.py。

  python mix_audio.py V1

- 画外音和同传：../02_配音/edit/tts_narration.wav（Fish 网页版「赛马娘（曼波欧耶版）」），高通 70 Hz + 两遍法 loudnorm 到 −16 LUFS（线性增益），
  按 TL.tts.blocks = [b0, b1, at, speed] 切块放进去（同传念不完的块带加速）。
- 发布会原声（素材/keynote_audio.weba，和画面同一起点）：先高通 90 Hz + 轻压缩 + loudnorm，再压到目标响度垫在下面：
  同传片段 −29 LUFS（听得见是谁在说、什么语气），画外音片段 −29 + gain_db（默认 −4 = −33 LUFS）；首尾各 0.04 s 淡入淡出；
  片段播放时 BGM 压低（×0.35，前后各 0.3 s 渐变）。
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav），全程垫在下面（−16 dB），不够长从第 48 s 起循环（交叉淡化 1.5 s），头 1 s 淡入、尾 2 s 淡出。
- 最后限幅 −1 dBTP。
"""
import json
import re
import subprocess
import sys
import wave

import numpy as np

from common import BGM, FPS, SRC_AUDIO, VOICE, out_dir

TTS = VOICE / "edit" / "tts_narration.wav"
SR = 48000
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
    ep = sys.argv[1]
    od = out_dir(ep)
    T = json.loads((od / "timeline.json").read_text(encoding="utf-8"))
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
        tgt = CLIP_LUFS + c.get("gain_db", 0)
        af = (f"highpass=f=90,acompressor=threshold=-34dB:ratio=3:attack=8:release=160:makeup=2,"
              f"loudnorm=I={tgt}:TP=-2.5:LRA=8")
        a = load(SRC_AUDIO, af=af, ss=c["in"], t=c["out"] - c["in"])
        cur = lufs_of(load(SRC_AUDIO, ss=c["in"], t=c["out"] - c["in"]))
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
        info.append(f"{cid} 原始 {cur:.1f} → {lufs_of(a):.1f} LUFS")
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
    (od / "audio").mkdir(exist_ok=True)
    with wave.open(str(od / "audio" / "mix.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(f"{ep} mix.wav {n / SR:.2f}s；配音原始 {tts_i} LUFS → {NARR_LUFS}；发布会原声 {'，'.join(info) or '无'}；整片 {lufs_of(mix):.1f} LUFS")


if __name__ == "__main__":
    main()
