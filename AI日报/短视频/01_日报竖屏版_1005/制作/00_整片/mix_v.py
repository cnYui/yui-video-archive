# -*- coding: utf-8 -*-
"""日报竖屏版混音 → audio/mix.wav（48 kHz 立体声，长度 = 整片帧数 / 30）。照短视频技能 mix_audio.py 的做法，这条没有素材原声，只有配音 + BGM：

- 配音：日报的 voice_main.wav（苏晓晓，t = 0 就是日报开场第一句，不重配），高通 70 Hz + 两遍法 loudnorm 到 −16 LUFS（线性增益）；
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav，lo-fi 轻爵士，492 s，整期够用不用循环），**比配音低约 14.5 dB**（技能第 13 条：bed 约 −7 … −11 dB，手机外放听得到；
  这首原始 −20 LUFS，床 −10.5 dB ≈ −30.5 LUFS）；没人说话的空档抬 +5 dB（0.4 s 渐变）；头 1 s 淡入、尾 2 s 淡出；
- 整体量到 −16 LUFS（频道惯例），个别超过 −1 dBFS 的采样点用软限幅压回去。
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
VOICE = Path(r"D:\大疆\AI日报\2026-10-05\制作\build\voice_main.wav")
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
SR = 48000
NARR_LUFS, TARGET_LUFS = -16.0, -16.0
BGM_REL_DB = -14.5          # BGM 比配音低多少（用 LUFS 量，按原始响度换算增益）
BGM_SWELL_DB = 5.0


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True)


def load(path, af=None):
    args = ["ffmpeg", "-v", "error", "-i", str(path), "-vn"]
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
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(p1[p1.rindex("{"): p1.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    return load(path, af), m["input_i"]


def activity(voice, n):
    """有人说话的地方 = 1：10 ms 一格的包络，前 0.12 s、后 0.4 s 保持，再平滑 0.15 s。"""
    hop = SR // 100
    k = n // hop
    m = voice[: k * hop].mean(1)
    rms = 20 * np.log10(np.sqrt((m.reshape(k, hop) ** 2).mean(1)) + 1e-9)
    act = (rms > -50).astype(np.float32)
    pad = np.pad(act, (12, 40))
    dil = np.array([pad[i: i + 53].max() for i in range(k)], np.float32)
    sm = np.convolve(dil, np.ones(15) / 15, mode="same")
    x = np.arange(n) / hop
    return np.interp(x, np.arange(k), sm).astype(np.float32)


def main():
    T = json.loads((HERE / "tl_v.json").read_text(encoding="utf-8"))
    n = T["frames"] * SR // T["fps"]
    voice = np.zeros((n, 2), np.float32)
    v, vin = normalized(VOICE)
    voice[: min(n, len(v))] = v[:n]
    act = activity(voice, n)
    # BGM：整期够长（492 s），从头放；按原始响度换算增益，使 BGM 比配音低 BGM_REL_DB
    b = load(BGM)[:n]
    assert len(b) >= n, "BGM 不够长，要循环"
    b_lufs = lufs_of(b)
    bed_db = (NARR_LUFS + BGM_REL_DB) - b_lufs
    swell = 1 + (10 ** (BGM_SWELL_DB / 20) - 1) * (1 - act)
    bgm = b * (10 ** (bed_db / 20)) * swell[:, None]
    bgm[:SR] *= np.linspace(0, 1, SR)[:, None]
    bgm[-2 * SR:] *= np.linspace(1, 0, 2 * SR)[:, None]
    mix = voice + bgm
    cur = lufs_of(mix)
    g = 10 ** ((TARGET_LUFS - cur) / 20)
    mix *= g
    lim = 10 ** (-1.0 / 20)
    over = np.abs(mix) > lim
    n_over = int(over.sum())
    mix[over] = np.sign(mix[over]) * (lim + (np.abs(mix[over]) - lim) * 0.2)
    mix = np.clip(mix, -lim, lim)
    out = HERE / "audio" / "mix.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    # QA：配音单路 / BGM 单路在成片里的响度，差值应约 14–15 dB
    vl, bl = lufs_of(voice * g), lufs_of(bgm * g)
    print(f"mix.wav {n / SR:.2f}s；配音原始 {vin} LUFS → {NARR_LUFS}；BGM 原始 {b_lufs:.1f} LUFS，床 {bed_db:+.1f} dB；"
          f"成片里配音单路 {vl:.1f} LUFS、BGM 单路 {bl:.1f} LUFS（差 {vl - bl:.1f} dB）；整片 {lufs_of(mix):.1f} LUFS，峰值 {20 * np.log10(float(np.abs(mix).max())):.1f} dBFS（软限幅 {n_over} 个采样点）")


if __name__ == "__main__":
    main()
