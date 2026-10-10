# -*- coding: utf-8 -*-
"""曼波同传（Fish 故事工作室空白项目 · 赛马娘（曼波欧耶版）· S2 Pro，一句一个区块）→ 逐句处理成 edit/lines/<id>.wav + edit/voice_lines.json。

  python build_voice.py [--speed 1.0]

输入：tts/seg_raw/final/NNNNNN.wav（import_segments.py 放进来的，顺序 = ../../台本/录制稿.json 的 lines）。
每句：转 48 kHz 单声道 → 去首尾静音（> −45 dB 才算有声音）→ 句内 ≥ 0.45 s 的停顿压成 0.30 s（同传要紧凑；曼波的句内停顿偏长）→ 音量拉到各句有声部分响度的中位数（最多 ±3 dB）
      → 首尾 8 ms 淡入淡出。默认不变速（技能 short-video：别靠加速凑时长）。
输出：edit/lines/<id>.wav；edit/voice_lines.json：每句 dur（秒）、raw_dur、cue_at（这句有多条字幕时，第 2、3… 条相对句首的开始秒数：在字宽占比位置附近找最近的能量低点，找不到就用占比）、gain_db、pauses_cut。
时间线（制作/00_整片/build_timeline.py）和混音（mix_audio.py）只读 voice_lines.json 和 edit/lines/。
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
sys.path.insert(0, str(Path(r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")))
from bilingual_std import zh_units  # noqa: E402

SR = 48000
THR_DB = -45.0
CUT_MIN, CUT_KEEP = 0.45, 0.30
MAXADJ = 3.0
FADE = int(0.008 * SR)


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def env_db(a, hop=0.01):
    h = int(SR * hop)
    n = len(a) // h
    return 20 * np.log10(np.sqrt((a[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)


def trim_and_cut(a):
    """去首尾静音、压句内长停顿 → (音频, 被压掉的停顿 [(位置秒, 原长秒)])。"""
    db = env_db(a)
    idx = np.where(db > THR_DB)[0]
    if len(idx) == 0:
        return a, []
    s0, e0 = idx[0], idx[-1] + 1
    keep = np.ones(len(db), bool)
    cuts, run = [], 0
    for k in range(s0, e0 + 1):
        if k < e0 and db[k] < -42:
            run += 1
        else:
            if run * 0.01 >= CUT_MIN:
                a0, a1 = k - run, k
                half = int(CUT_KEEP * 50)                       # 保留的 0.30 s 两头各一半
                if a1 - half > a0 + half:
                    keep[a0 + half: a1 - half] = False
                    cuts.append((round((a0 - s0) * 0.01, 2), round(run * 0.01, 2)))
            run = 0
    h = int(SR * 0.01)
    pieces, k = [], s0
    while k < e0:
        j = k
        while j < e0 and keep[j] == keep[k]:
            j += 1
        if keep[k]:
            pieces.append(a[k * h: j * h])
        k = j
    out = pieces[0]
    xf = int(0.010 * SR)
    for p in pieces[1:]:
        r = np.linspace(0, 1, xf)
        out = np.concatenate([out[:-xf], out[-xf:] * (1 - r) + p[:xf] * r, p[xf:]])
    return out, cuts


def rms_db(a):
    return 20 * np.log10(np.sqrt((a ** 2).mean()) + 1e-9)


def write_wav(path, a):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())


def snap_to_dip(a, t_est, win=0.35):
    """在 t_est ± win 内找最近的能量低点（80 ms 滑窗最小）；没有明显低点（比整句低 12 dB 以上）就返回 None。"""
    h = int(0.08 * SR)
    lo, hi = max(0, int((t_est - win) * SR)), min(len(a) - h, int((t_est + win) * SR))
    if hi <= lo:
        return None
    best, bt = 1e9, None
    for p in range(lo, hi, int(0.01 * SR)):
        e = rms_db(a[p: p + h])
        if e < best:
            best, bt = e, p / SR + 0.04
    return bt if best < rms_db(a) - 12 else None


def main():
    speed = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else 1.0
    lines = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
    files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
    assert len(files) == len(lines), f"{len(files)} 个文件，台本 {len(lines)} 句"
    out_dir = HERE / "edit" / "lines"
    out_dir.mkdir(parents=True, exist_ok=True)
    cut = []
    for f in files:
        a, cuts = trim_and_cut(load(f))
        cut.append((a, cuts))
    rms = [rms_db(a) for a, _ in cut]
    med = float(np.median(rms))
    res, total = [], 0.0
    for l, (a, cuts), lv in zip(lines, cut, rms):
        adj = float(np.clip(med - lv, -MAXADJ, MAXADJ))
        a = a * (10 ** (adj / 20))
        a[:FADE] *= np.linspace(0, 1, FADE)
        a[-FADE:] *= np.linspace(1, 0, FADE)
        raw_p = out_dir / f"{l['id']}_raw.wav"
        write_wav(raw_p, a)
        dst = out_dir / f"{l['id']}.wav"
        flt = [] if abs(speed - 1.0) < 1e-6 else ["-filter:a", f"atempo={speed}"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw_p), *flt, "-ar", str(SR), "-ac", "1", str(dst)], check=True)
        raw_p.unlink()
        b = load(dst)
        dur = len(b) / SR
        cue_at, parts = [], l["zh"]
        if len(parts) > 1:
            tot_u = sum(zh_units(z) for z in parts)
            acc = 0.0
            for z in parts[:-1]:
                acc += zh_units(z)
                est = dur * acc / tot_u
                t = snap_to_dip(b, est)
                cue_at.append(round(t if t is not None else est, 3))
        res.append({"id": l["id"], "dur": round(dur, 3), "cue_at": cue_at, "gain_db": round(adj, 2), "pauses_cut": cuts, "say": l["say"]})
        total += dur
        print(f"{l['id']}  {dur:5.2f} s  调 {adj:+5.2f} dB  压停顿 {cuts}  字幕起点 {cue_at}  {l['say']}")
    (HERE / "edit" / "voice_lines.json").write_text(json.dumps({"speed": speed, "total": round(total, 3), "lines": res}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"合计 {total:.2f} s（speed {speed}），响度中位数 {med:.1f} dB")


if __name__ == "__main__":
    main()
