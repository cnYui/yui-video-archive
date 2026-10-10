# -*- coding: utf-8 -*-
"""成片混音 → audio/mix.wav（48 kHz 立体声，长度 = 成片帧数 / 30）。做法照 Way to AGI 02 期的 mix_audio.py。

- 人声：../02_出镜/edit/narration.wav（build_edit.py 已按来源统一电平：出镜的 DJI 声音和录屏里的电脑麦克风声音）；
  高通 70 Hz，两遍法 loudnorm 到 −16 LUFS（线性增益，不改动态）。
- BGM：系列 BGM（AI科普/素材/音频/bgm.wav，母带 −20 LUFS，16 小节 48 s 一轮）。全程 −15 dB 垫在下面；
  快进（AI 在生成、没有人声）的地方抬到 −8 dB，前后 0.5 s 过渡；不够长就从第 48 s 起循环（交叉淡化 1.5 s）；结尾淡出。
- 最后限幅 −1 dBTP。
"""
import json
import re
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CUT = HERE.parent / "02_出镜"
BGM = Path(r"D:\大疆\AI科普\素材\音频\bgm.wav")
SR, FPS = 48000, 30
NARR_LUFS = -16.0
BGM_BED, BGM_FAST = -15.0, -8.0


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True)


def load(path, af=None):
    args = ["ffmpeg", "-v", "error", "-i", str(path), "-vn"]
    if af:
        args += ["-af", af]
    args += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(run(args).stdout, dtype=np.float32).reshape(-1, 2).copy()


def write_wav(path, a):
    path.parent.mkdir(exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


def lufs(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def main():
    ed = json.loads((CUT / "edit" / "edit.json").read_text(encoding="utf-8"))
    n = ed["frames"] * SR // FPS
    # 人声：高通 + 两遍法 loudnorm
    narr_path = CUT / "edit" / "narration.wav"
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(narr_path), "-af",
                         f"highpass=f=70,loudnorm=I={NARR_LUFS}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(p1[p1.rindex("{"): p1.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={NARR_LUFS}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    voice = load(narr_path, af)
    voice = np.pad(voice, ((0, max(0, n - len(voice))), (0, 0)))[:n]
    # BGM：不够长就从 48 s 起循环
    b = load(BGM)
    xf = int(1.5 * SR)
    out = b[: 480 * SR].copy()
    loop = b[48 * SR: 480 * SR]
    while len(out) < n + SR:
        ramp = np.linspace(0, 1, xf)[:, None]
        tail = out[-xf:] * (1 - ramp) + loop[:xf] * ramp
        out = np.concatenate([out[:-xf], tail, loop[xf:]])
    bgm = out[:n]
    # 增益包络：平时 BGM_BED，快进时 BGM_FAST
    g = np.full(ed["frames"], BGM_BED, np.float32)
    for c in ed["clips"]:
        if c["kind"] == "fast" and c["n"] >= 6:
            g[c["out0"]: c["out0"] + c["n"]] = BGM_FAST
    k = int(0.5 * FPS)
    g = np.convolve(np.pad(g, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="valid")
    gs = np.interp(np.arange(n) / SR * FPS, np.arange(len(g)), g)
    bgm *= (10 ** (gs / 20))[:, None]
    # 开头 1 s 淡入、结尾 2 s 淡出
    bgm[: SR] *= np.linspace(0, 1, SR)[:, None]
    bgm[-2 * SR:] *= np.linspace(1, 0, 2 * SR)[:, None]
    mix = voice + bgm
    peak = np.abs(mix).max()
    lim = 10 ** (-1.0 / 20)
    if peak > lim:
        # 简单的软限幅：只压超过的部分
        over = np.abs(mix) > lim
        mix[over] = np.sign(mix[over]) * (lim + (np.abs(mix[over]) - lim) * 0.2)
        mix = np.clip(mix, -lim, lim)
    write_wav(HERE / "audio" / "mix.wav", mix)
    print(f"mix.wav {n / SR:.2f}s  人声 {lufs(narr_path):.1f} → 成片 {lufs(HERE / 'audio' / 'mix.wav'):.1f} LUFS")


if __name__ == "__main__":
    main()
