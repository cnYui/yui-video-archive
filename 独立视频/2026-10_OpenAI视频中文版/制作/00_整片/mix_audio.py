# -*- coding: utf-8 -*-
"""混音 → audio/mix.wav（48 kHz 立体声，长度 = 成片时长）。做法照白宫那条：

- 中文配音：../02_配音/edit/tts_narration.wav（Fish 网页版「赛马娘（曼波欧耶版）」），高通 70 Hz + 两遍法 loudnorm 到 −16 LUFS（线性增益），
  按 timeline.json 的 tts.blocks = [b0, b1, at, speed] 切块放进去。
- 英文原声：压到 −29 LUFS 垫在下面（还听得见是谁在说、什么语气）；没有中文的空档（≥ GAP_MIN 秒）把原声抬 GAP_BOOST_DB，让现场的声音（打字、电话铃、笑声）露出来；
  头 0.3 s 淡入、尾 1.5 s 淡出。
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
ORIG = EP / "素材" / "fHEIw5CcN5U_audio_en.webm"
SR = 48000
NARR_LUFS, BED_LUFS = -16.0, -29.0
GAP_MIN, GAP_BOOST_DB, RAMP = 1.5, 6.0, 0.4


def run(args):
    return subprocess.run([str(a) for a in args], check=True, capture_output=True)


def load(path, af=None):
    args = ["ffmpeg", "-v", "error", "-i", str(path), "-vn"]
    if af:
        args += ["-af", af]
    args += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(run(args).stdout, dtype=np.float32).reshape(-1, 2).copy()


def stretch(a, speed):
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", f"atempo={speed:.4f}",
                        "-f", "f32le", "-ar", str(SR), "-ac", "2", "-"], input=a.astype(np.float32).tobytes(), capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32).reshape(-1, 2).copy()


def lufs_of(a):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128=framelog=quiet:peak=true", "-f", "null", "-"],
                       input=a.astype(np.float32).tobytes(), capture_output=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", p.stderr.decode("utf-8", "replace"))[-1])


def normalized(path, target=NARR_LUFS):
    p1 = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    m = json.loads(p1[p1.rindex("{"): p1.rindex("}") + 1])
    af = (f"highpass=f=70,loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    return load(path, af), m["input_i"]


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    n = int(round(T["total"] * SR))
    voice = np.zeros((n, 2), np.float32)
    tts, tts_i = normalized(TTS)
    for b0, b1, at, speed in T["tts"]["blocks"]:
        seg = tts[int(round(b0 * SR)): int(round(b1 * SR))]
        if abs(speed - 1.0) > 1e-3:
            seg = stretch(seg, speed)
        k = int(round(at * SR))
        if k < 0:
            seg, k = seg[-k:], 0
        voice[k: k + len(seg)] += seg[: max(0, n - k)]
    orig = load(ORIG)
    cur = lufs_of(orig)
    gain = 10 ** ((BED_LUFS - cur) / 20)
    bed = np.zeros((n, 2), np.float32)
    m = min(n, len(orig))
    bed[:m] = orig[:m] * gain
    # 空档抬升：中文没在说话的地方（相邻两句配音之间 ≥ GAP_MIN 秒），把原声抬 GAP_BOOST_DB，前后各 RAMP 秒渐变
    spans = sorted((c["s"] - 0.15, c["e"] + 0.15) for c in T["cues"])
    env = np.ones(n, np.float32)
    boost = 10 ** (GAP_BOOST_DB / 20)
    gaps, prev = [], 0.0
    for s, e in spans + [(T["total"] + 5, T["total"] + 6)]:
        if s - prev >= GAP_MIN:
            gaps.append((prev, s))
        prev = max(prev, e)
    r = int(RAMP * SR)
    for g0, g1 in gaps:
        a, b = int(g0 * SR), min(n, int(g1 * SR))
        if b - a < 2 * r:
            continue
        env[a + r: b - r] = boost
        env[a: a + r] = np.linspace(1, boost, r)
        env[b - r: b] = np.linspace(boost, 1, r)
    bed *= env[:, None]
    f = int(0.3 * SR)
    bed[:f] *= np.linspace(0, 1, f)[:, None]
    bed[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))[:, None]
    mix = voice + bed
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
    print(f"mix.wav {n / SR:.2f}s；配音原始 {tts_i} LUFS → {NARR_LUFS}；原声 {cur:.1f} LUFS → {BED_LUFS}（空档 {len(gaps)} 处抬 {GAP_BOOST_DB:g} dB）；整片 {lufs_of(mix):.1f} LUFS，峰值 {20 * np.log10(float(np.abs(mix).max())):.1f} dBFS")


if __name__ == "__main__":
    main()
