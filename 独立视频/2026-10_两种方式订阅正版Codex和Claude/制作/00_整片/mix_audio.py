# -*- coding: utf-8 -*-
"""整片混音 → audio/mix.wav（48 kHz 立体声，长度 = 整片帧数 / 30）。做法照《从0到1用WorkBuddy上线一个微信小程序》的 mix_audio.py。

- 人声两条，各自高通 70 Hz + 两遍法 loudnorm 到 −16 LUFS（线性增益）：
  - 开场真人出镜：../02_出镜/edit/cam_narration.wav（DJI 0163 剪好的口播），放在 TL.cam.t0；
  - 演示：../02_出镜/edit/tts_narration.wav（克隆声音「悠一」），按 TL.tts.blocks 分块放（换章节处多留了停顿）。
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav），全程 −16 dB 垫在下面，不够长从第 48 s 起循环（交叉淡化 1.5 s），头 1 s 淡入、尾 2 s 淡出。
- 最后限幅 −1 dBTP。
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CUT = HERE.parent / "02_出镜" / "edit"
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
SR, FPS = 48000, 30
NARR_LUFS, BGM_BED = -16.0, -16.0


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True)


def load(path, af=None):
    args = ["ffmpeg", "-v", "error", "-i", str(path), "-vn"]
    if af:
        args += ["-af", af]
    args += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(run(args).stdout, dtype=np.float32).reshape(-1, 2).copy()


def lufs(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def normalized(path):
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                         f"highpass=f=70,loudnorm=I={NARR_LUFS}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(p1[p1.rindex("{"): p1.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={NARR_LUFS}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    return load(path, af), m["input_i"]


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    n = T["frames"] * SR // FPS
    voice = np.zeros((n, 2), np.float32)
    cam, cam_i = normalized(CUT / "cam_narration.wav")
    k = int(round(T["cam"]["t0"] * SR))
    voice[k: k + len(cam)] += cam[: max(0, n - k)]
    tts, tts_i = normalized(CUT / "tts_narration.wav")
    for b0, b1, off in T["tts"]["blocks"]:
        seg = tts[int(round(b0 * SR)): int(round(b1 * SR))]
        k = int(round(off * SR))
        voice[k: k + len(seg)] += seg[: max(0, n - k)]
    b = load(BGM)
    xf = int(1.5 * SR)
    out = b.copy()
    loop = b[48 * SR:]
    while len(out) < n + SR:
        ramp = np.linspace(0, 1, xf)[:, None]
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - ramp) + loop[:xf] * ramp, loop[xf:]])
    bgm = out[:n] * (10 ** (BGM_BED / 20))
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
    print(f"mix.wav {n / SR:.2f}s；出镜原始 {cam_i} LUFS、克隆配音原始 {tts_i} LUFS → 各 {NARR_LUFS}；整片 {lufs(HERE / 'audio' / 'mix.wav'):.1f} LUFS")


if __name__ == "__main__":
    main()
