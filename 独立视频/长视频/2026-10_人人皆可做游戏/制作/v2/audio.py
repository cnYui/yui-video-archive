# -*- coding: utf-8 -*-
"""audio.py —— 成片的声音：人声 + 游戏 BGM + 游戏音效 + 背景乐，四条分轨，加一条混音。
  python audio.py          → 音轨/人声.wav 游戏BGM.wav 游戏音效.wav 背景乐.wav 混音.wav（48 kHz 立体声，都从 0 秒对齐画面）

  - 人声 = voice.py 渲好的 人声.wav（−16 LUFS）。
  - 游戏声：plan.py 里每个实机镜头登记的 (t0, t1, 录像段, 起点秒, 模式)；BGM / 音效各取各的轨（full.webm 的声音比画面晚 0.03–0.08 秒开始，bgm / sfx 要往回挪，和 make_clips.py 同一套）。
    under = 垫在人声下面（BGM −15 dB、音效 −12 dB）；full = 只有游戏声（开场快切、“眼睛特写 → 打穿墙”那 10 秒），原音量。
  - 背景乐 = 游戏自己合成的 comedy.wav 循环，只在没有实机声音的口播段垫着（−27 dB），进出各 0.6 秒淡。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))

import plan  # noqa: E402
import voice  # noqa: E402

SR = 48000
OUT = ROOT / "音轨"
BED = Path(r"D:\大疆\游戏素材\银魂\音频\音乐_a\comedy.wav")


def db(x):
    return 10 ** (x / 20)


def audio_offset(d: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=start_time", "-of", "csv=p=0", str(d / "full.webm")], capture_output=True, text=True).stdout.strip()
    try:
        return float(r)
    except ValueError:
        return 0.0


def cut(webm: Path, a: float, dur: float) -> np.ndarray:
    """webm 的 [a, a+dur] → 立体声 float32（a < 0 的部分补静音，长度严格 = dur）。"""
    n = int(round(dur * SR))
    out = np.zeros((n, 2), np.float32)
    lead = max(0.0, -a)
    if dur - lead <= 0:
        return out
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % max(0.0, a), "-t", "%.3f" % (dur - lead), "-i", str(webm), "-vn", "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"],
                       capture_output=True)
    y = np.frombuffer(r.stdout, np.float32).reshape(-1, 2)
    i = int(round(lead * SR))
    m = min(len(y), n - i)
    out[i:i + m] = y[:m]
    return out


def fade(y: np.ndarray, t_in: float = 0.12, t_out: float = 0.12) -> np.ndarray:
    y = y.copy()
    a, b = min(len(y) // 2, int(t_in * SR)), min(len(y) // 2, int(t_out * SR))
    if a:
        y[:a] *= np.linspace(0, 1, a, dtype=np.float32)[:, None]
    if b:
        y[len(y) - b:] *= np.linspace(1, 0, b, dtype=np.float32)[:, None]
    return y


def main():
    T = plan.build()
    T.close()
    cues = list(plan.AUDIO)
    total = voice.total(voice.timeline())
    n = int((total + 1.0) * SR)
    bgm = np.zeros((n, 2), np.float32)
    sfx = np.zeros((n, 2), np.float32)
    off_cache = {}
    for t0, t1, ch, st, mode in cues:
        d = plan.CH[ch].parent
        off = off_cache.setdefault(ch, audio_offset(d))
        dur = t1 - t0
        g_b, g_s = (-2.0, -7.0) if mode == "full" else (-15.0, -12.0)
        for k, g, buf in (("bgm", g_b, bgm), ("sfx", g_s, sfx)):
            y = fade(cut(d / (k + ".webm"), st - off, dur)) * db(g)
            i = int(round(t0 * SR))
            m = min(len(y), n - i)
            buf[i:i + m] += y[:m]
    # 背景乐：没有实机声音的时候垫着
    bed = np.zeros((n, 2), np.float32)
    if BED.exists():
        y, sr = sf.read(str(BED), dtype="float32", always_2d=True)
        if y.shape[1] == 1:
            y = np.repeat(y, 2, axis=1)
        assert sr == SR or True
        if sr != SR:
            r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(BED), "-ar", str(SR), "-ac", "2", "-f", "f32le", "-"], capture_output=True)
            y = np.frombuffer(r.stdout, np.float32).reshape(-1, 2)
        reps = int(np.ceil(n / len(y)))
        loop = np.tile(y, (reps, 1))[:n] * db(-27.0)
        env = np.ones(n, np.float32)
        for t0, t1, ch, st, mode in cues:
            a, b = int(max(0.0, t0 - 0.3) * SR), int(min(total + 1, t1 + 0.3) * SR)
            env[a:b] = 0.0
        # 平滑（0.6 秒）
        k = int(0.6 * SR)
        env = np.convolve(env, np.ones(k, np.float32) / k, mode="same")
        # 开场快切之前不垫，片尾之后不垫
        env[: int(voice.PRE * SR)] = 0.0
        bed = loop * env[:, None]
    # 人声
    v, sr = sf.read(str(ROOT / "人声.wav"), dtype="float32", always_2d=True)
    assert sr == SR
    voice_t = np.zeros((n, 2), np.float32)
    voice_t[:min(n, len(v))] = v[:n]
    OUT.mkdir(exist_ok=True)
    for name, y in (("人声", voice_t), ("游戏BGM", bgm), ("游戏音效", sfx), ("背景乐", bed)):
        sf.write(str(OUT / (name + ".wav")), y[: int((total + 0.5) * SR)], SR, subtype="PCM_16")
    mix = voice_t + bgm + sfx + bed
    raw = OUT / "_mix_raw.wav"
    sf.write(str(raw), np.clip(mix[: int((total + 0.5) * SR)], -1, 1), SR, subtype="PCM_16")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", str(SR), "-c:a", "pcm_s16le", str(OUT / "混音.wav")], check=True)
    raw.unlink()
    print("done", OUT, "cues", len(cues))


if __name__ == "__main__":
    main()
