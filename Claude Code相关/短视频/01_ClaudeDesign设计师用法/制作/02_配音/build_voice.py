# -*- coding: utf-8 -*-
"""配音（Fish 故事工作室·赛马娘（曼波欧耶版）·S2 Pro，一句一个区块）→ 逐句处理成 edit/lines/<id>.wav + edit/voice_lines.json。

  python build_voice.py [--speed 1.0]

输入：tts/seg_raw/final/NNNNNN.wav（import_segments.py 放进来的，顺序 = ../../台本/录制稿.json 的 lines）。
每句：转 48 kHz 单声道 → 去首尾静音（> −45 dB 的才算有声音）→ 句内 ≥ 0.30 s 的停顿压成 0.20 s（短视频要快：曼波的逗号停顿偏长）→
      音量拉到各句有声部分响度的中位数（最多 ±3 dB）→（只有 --speed ≠ 1 时）整句 atempo 变速 → 首尾 8 ms 淡入淡出。
      默认 1.0×：技能 short-video 规定“别靠加速凑时长”（最多 1.1×，要用户同意），所以第 1 条的做法是删句、不加速（第一版配音试过 1.15×，作废）。
输出：edit/lines/<id>.wav（48 kHz 单声道 16 bit，已加速）；edit/voice_lines.json：每句 dur（加速后的秒数）、cue_at（多条字幕时，第 2、3…条相对句首的开始秒数，
      在整句宽度占比的位置附近找最近的能量低点，找不到就用占比）、gain_db、pauses_cut。
时间线 / 混音（制作/00_整片/build_timeline.py）读 voice_lines.json，不再碰原始区块。
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
CUT_MIN, CUT_KEEP = 0.30, 0.20          # 句内停顿 ≥ 0.30 s 的压成 0.20 s
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
    keep_mask = np.ones(len(db), bool)
    cuts, run = [], 0
    for k in range(s0, e0 + 1):
        quiet = k < e0 and db[k] <= THR_DB - 0 and True
        quiet = k < e0 and db[k] < -42
        if quiet:
            run += 1
        else:
            if run * 0.01 >= CUT_MIN:
                a0, a1 = k - run, k                      # 停顿的帧范围
                drop0, drop1 = a0 + int(CUT_KEEP * 50), a1 - int(CUT_KEEP * 50)     # 两头各留 0.10 s
                if drop1 > drop0:
                    keep_mask[drop0:drop1] = False
                    cuts.append((round((a0 - s0) * 0.01, 2), round(run * 0.01, 2)))
            run = 0
    h = int(SR * 0.01)
    pieces, k = [], s0
    while k < e0:
        j = k
        while j < e0 and keep_mask[j] == keep_mask[k]:
            j += 1
        if keep_mask[k]:
            pieces.append(a[k * h: j * h])
        k = j
    out = pieces[0]
    xf = int(0.010 * SR)
    for p in pieces[1:]:                                   # 10 ms 交叉淡化
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


def snap_to_dip(a, t_est, win=0.30):
    """在 t_est ± win 内找最近的能量低点（80 ms 滑窗最小），返回时刻秒；没有明显低点就返回 None。"""
    h = int(0.08 * SR)
    lo, hi = max(0, int((t_est - win) * SR)), min(len(a) - h, int((t_est + win) * SR))
    if hi <= lo:
        return None
    best, bt = 1e9, None
    for p in range(lo, hi, int(0.01 * SR)):
        e = rms_db(a[p: p + h])
        if e < best:
            best, bt = e, p / SR + 0.04
    ref = rms_db(a)
    return bt if best < ref - 12 else None


def main():
    speed = 1.0                              # 技能 short-video 的规矩：别靠加速凑时长（最多 1.1×，要用户同意），超长就删句
    if "--speed" in sys.argv:
        speed = float(sys.argv[sys.argv.index("--speed") + 1])
    lines = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
    files = sorted((HERE / "tts" / "seg_raw" / "final").glob("*.wav"))
    assert len(files) == len(lines), f"{len(files)} 个文件，台本 {len(lines)} 句"
    out_dir = HERE / "edit" / "lines"
    out_dir.mkdir(parents=True, exist_ok=True)
    cut, rms = [], []
    for f in files:
        a, cuts = trim_and_cut(load(f))
        cut.append((a, cuts))
        rms.append(rms_db(a))
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
        b = load(dst)
        dur = len(b) / SR
        # 多条字幕：第 k+1 条的开始时刻（句内）
        cue_at = []
        cues = l["cues"]
        if len(cues) > 1:
            tot_u = sum(zh_units(c["zh"]) for c in cues)
            acc = 0.0
            for c in cues[:-1]:
                acc += zh_units(c["zh"])
                est = dur * acc / tot_u
                t = snap_to_dip(b, est)
                cue_at.append(round(t if t is not None else est, 3))
        res.append({"id": l["id"], "dur": round(dur, 3), "raw_dur": round(len(a) / SR, 3), "cue_at": cue_at, "gain_db": round(adj, 2), "pauses_cut": cuts})
        total += dur
        raw_p.unlink()
        print(f"{l['id']}  {dur:5.2f} s（加速前 {len(a) / SR:5.2f} s）  调 {adj:+5.2f} dB  压掉停顿 {cuts}  字幕起点 {cue_at}  {l['say']}")
    (HERE / "edit" / "voice_lines.json").write_text(json.dumps({"speed": speed, "total": round(total, 3), "lines": res}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"合计 {total:.2f} s（speed {speed}），响度中位数 {med:.1f} dB")


if __name__ == "__main__":
    main()
