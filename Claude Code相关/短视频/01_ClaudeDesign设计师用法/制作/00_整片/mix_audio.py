# -*- coding: utf-8 -*-
"""混音：02_配音/edit/lines/<id>.wav 按 timeline.json 的开口时刻放进一条 48 kHz 立体声轨 → build/audio.wav。

  python mix_audio.py

只有曼波中文配音（原片的英文原声不留）。响度：整条拉到 −16 LUFS（项目口播标准），峰值限在 −1.5 dBFS（alimiter），首尾各 10 ms 淡入淡出。
"""
import json
import re
import subprocess
import wave

import numpy as np

import config as C

BUILD = C.HERE / "build"
SR = 48000
TARGET_LUFS = -16.0


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def write_wav(path, a):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


def measure(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    i = re.findall(r"\n\s+I:\s+(-?\d+\.\d) LUFS", txt)
    p = re.findall(r"Peak:\s+(-?\d+\.\d) dBFS", txt)
    return (float(i[-1]) if i else None), (float(p[-1]) if p else None)


def main():
    tl = json.loads((BUILD / "timeline.json").read_text(encoding="utf-8"))
    n = int(round((tl["total"] + 0.3) * SR))
    mix = np.zeros((n, 2), np.float32)
    for r in tl["lines"]:
        a = load(C.EP / "制作" / "02_配音" / "edit" / "lines" / f"{r['id']}.wav")
        s = int(round(r["onset"] * SR))
        mix[s: s + len(a), 0] += a[: n - s]
        mix[s: s + len(a), 1] += a[: n - s]
    raw_p = BUILD / "audio_raw.wav"
    write_wav(raw_p, mix)
    lufs, peak = measure(raw_p)
    gain = TARGET_LUFS - lufs
    out_p = BUILD / "audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw_p), "-af", f"volume={gain:.2f}dB,alimiter=limit=0.84:attack=3:release=40:level=disabled", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(out_p)], check=True)
    l2, p2 = measure(out_p)
    print(f"拉前 {lufs} LUFS（峰值 {peak} dBFS）→ 增益 {gain:+.2f} dB → {l2} LUFS（峰值 {p2} dBFS）；{out_p}")


if __name__ == "__main__":
    main()
