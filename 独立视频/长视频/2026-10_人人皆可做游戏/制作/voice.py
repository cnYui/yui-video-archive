# -*- coding: utf-8 -*-
"""口播剪辑表（EDL）：把四条出镜口播剪成一条连续的人声，并告诉别的模块“某条素材的第 t 秒 = 成片的第几秒”。

  python voice.py show        打印每个 ASR 句子在成片里的起止（做画面、字幕时对时间用）
  python voice.py audio       渲出 人声.wav（48 kHz 立体声，−16 LUFS）
  python voice.py face        渲出 face_tl.mp4（出镜画面，和成片同一条时间轴，空档是黑的）

剪法（用户 2026-10-06：露脸素材到了，“asr 后开始微调”）：
  - 只剪气口：两句话之间超过 0.40 秒的静音压成 0.30 秒（切点落在静音里，前后各留 0.15 秒气口），不动字；
  - 整句删掉的：下面 CUTS 里列了（口头准备的“好，那么来说个尾吧”、“谢谢观看”、说了一半的“因为”、“就是”）；
  - 四条之间、段落之间的过渡停顿由 GAPS 给（秒）。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
FACE = HERE / "02_出镜"
CLIPS = ["0190", "0191", "0193", "0194"]

# 保留哪些源时间段（每条素材一组），按稿子顺序；(开始, 结束, 段落)
KEEP = [
    ("0190", 0.7, 60.4, "S01"),
    ("0191", 0.8, 27.9, "S03"),
    ("0193", 0.0, 30.2, "S03"),
    ("0193", 32.2, 58.1, "S04"),
    ("0193", 58.5, 115.9, "S05"),
    ("0193", 117.9, 147.2, "S06"),
    ("0194", 0.7, 35.86, "S08"),
    ("0194", 37.7, 94.9, "S10"),
    ("0194", 101.3, 110.0, "S11"),
]
# 段内再删掉的小段（源时间）：说了一半的、口头禅
CUTS = {
    "0193": [(129.85, 132.52)],                              # “然后在沙发里，”（说了一半重来）
    "0194": [(4.90, 5.98), (28.0, 28.95), (31.39, 32.4),     # “将 | 近五分钟”中间的停顿、“然后银魂，”（说了一半重来）、“就是”（从“飞”和“就是”之间的能量谷 31.39 切）
             (88.80, 89.12)],                                # “通过这 | 种 AI 工具”：他在“这”后面停了半秒，压到 0.12 秒
}
HARD_END = {("0194", 35.86): 35.86}           # “…蛮有意思的 | 因为”：到“的”为止，不要把后面的“因为”带进来
# 每一段开头前插入的停顿（秒）：不同段之间喘口气 / 给片名卡、游戏原声留位置
GAPS = {"S01": 0.0, "S03": 1.2, "S04": 0.55, "S05": 0.45, "S06": 0.55, "S08": 11.5, "S10": 0.7, "S11": 0.7}
PRE = 4.0                      # 开场前先放 4 秒实机快切（没有人声，只有游戏原声）
FQ = 60                        # 所有切点落在 1/60 秒的网格上，音频和画面一帧不差

PAUSE_MAX, PAUSE_KEEP, BREATH = 0.40, 0.30, 0.15
SR = 48000


def load_env(clip: str):
    y, sr = sf.read(str(FACE / "audio16" / f"{clip}.wav"))
    hop = 160
    n = len(y) // hop
    rms = np.sqrt((y[:n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms)          # 每 10 ms 一个值


def silences(db: np.ndarray, a: float, b: float, thr=-48.0, min_len=0.12):
    """[a, b] 内连续低于 thr 的区间 [(s, e)]（秒）。"""
    i0, i1 = int(a * 100), int(b * 100)
    low = db[i0:i1] < thr
    out, start = [], None
    for k, v in enumerate(low):
        if v and start is None:
            start = k
        if (not v or k == len(low) - 1) and start is not None:
            end = k if not v else k + 1
            if (end - start) / 100 >= min_len:
                out.append((a + start / 100, a + end / 100))
            start = None
    return out


def build_pieces():
    """→ [(clip, src_in, src_out, section)]：压过停顿、删过小段后的片段，按成片顺序。"""
    envs = {c: load_env(c) for c in CLIPS}
    pieces = []
    for clip, a, b, sec in KEEP:
        db = envs[clip]
        cuts = [(s, e) for s, e in CUTS.get(clip, []) if s >= a and e <= b]
        # 要切掉的区间 = 长静音的中段 + CUTS
        gone = []
        for s, e in silences(db, a, b):
            if e - s > PAUSE_MAX:
                gone.append((s + PAUSE_KEEP / 2, e - PAUSE_KEEP / 2))
        gone += cuts
        gone.sort()
        # 合并重叠
        merged = []
        for s, e in gone:
            if merged and s <= merged[-1][1] + 1e-6:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        # 起止都落在静音里：起点往前找到气口，终点往后留气口
        start = a
        sil = silences(db, max(0, a - 0.6), a + 0.6)
        for s, e in sil:
            if s <= a + 0.05 <= e + 0.3:
                start = max(s, e - BREATH) if e <= a + 0.6 else a
        end = b
        for s, e in silences(db, b - 0.3, min(len(db) / 100 - 0.01, b + 0.8)):
            if s >= b - 0.35:
                end = min(e, s + BREATH + 0.05)
                break
        end = min(end, HARD_END.get((clip, b), end))
        cur = start
        for s, e in merged:
            if s > cur + 0.05:
                pieces.append((clip, round(cur, 3), round(s, 3), sec))
            cur = max(cur, e)
        if end > cur + 0.05:
            pieces.append((clip, round(cur, 3), round(end, 3), sec))
    return pieces


def q(x: float) -> float:
    return round(x * FQ) / FQ


def timeline():
    """→ [{'clip','src_in','src_out','sec','out_in','out_out'}]（成片秒数，已含 PRE 秒开场；全部落在 1/60 秒网格上）"""
    pieces = build_pieces()
    t = PRE
    out, last_sec = [], None
    for clip, a, b, sec in pieces:
        if sec != last_sec:
            t += GAPS.get(sec, 0.4) if out else 0.0
            last_sec = sec
        elif out and out[-1]["clip"] != clip:
            t += 0.35
        t = q(t)
        d = max(1, round((b - a) * FQ)) / FQ
        out.append({"clip": clip, "src_in": a, "src_out": round(a + d, 4), "sec": sec, "out_in": t, "out_out": round(t + d, 4)})
        t = round(t + d, 4)
    return out


def out_time(tl, clip: str, src_t: float) -> float | None:
    """素材 clip 的第 src_t 秒 → 成片秒数；落在被删掉的地方就返回离得最近的那一端。"""
    best = None
    for p in tl:
        if p["clip"] != clip:
            continue
        if p["src_in"] - 1e-6 <= src_t <= p["src_out"] + 1e-6:
            return p["out_in"] + (src_t - p["src_in"])
        d = min(abs(src_t - p["src_in"]), abs(src_t - p["src_out"]))
        if best is None or d < best[0]:
            best = (d, p["out_in"] if abs(src_t - p["src_in"]) < abs(src_t - p["src_out"]) else p["out_out"])
    return best[1] if best else None


def total(tl):
    return tl[-1]["out_out"]


def render_audio(tl, out_wav: Path, lufs=-16.0):
    """按 EDL 把 audio/<编号>.wav（48 kHz 立体声）拼起来，每个接缝做 8 ms 淡入淡出，最后归一到 lufs。"""
    n = int((total(tl) + 0.5) * SR)
    buf = np.zeros((n, 2), np.float32)
    cache = {}
    fade = int(0.008 * SR)
    for p in tl:
        if p["clip"] not in cache:
            y, sr = sf.read(str(FACE / "audio" / f"{p['clip']}.wav"), dtype="float32")
            assert sr == SR
            cache[p["clip"]] = y
        y = cache[p["clip"]]
        seg = y[int(p["src_in"] * SR):int(p["src_out"] * SR)].copy()
        k = min(fade, len(seg) // 2)
        seg[:k] *= np.linspace(0, 1, k, dtype=np.float32)[:, None]
        seg[len(seg) - k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]
        i = int(p["out_in"] * SR)
        buf[i:i + len(seg)] += seg
    tmp = out_wav.with_suffix(".raw.wav")
    sf.write(str(tmp), buf, SR, subtype="PCM_16")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=7", "-ar", str(SR), "-c:a", "pcm_s16le", str(out_wav)], check=True)
    tmp.unlink()


def face_timeline(tl, out_mp4: Path, size=(1152, 648)):
    """把出镜画面按同一份剪辑表接成一条和成片同一时间轴的 face_tl.mp4（没人声的空档是黑的）。
    每条素材只解一遍码（select 只留要用的帧），逐片段按帧数取，所以帧数和人声音频一帧不差。"""
    w, h = size
    fb = w * h * 3 // 2
    black = bytes([16]) * (w * h) + bytes([128]) * (w * h // 2)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", "%dx%d" % size, "-r", str(FQ), "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-g", "30", "-pix_fmt", "yuv420p", str(out_mp4)], stdin=subprocess.PIPE)
    cur = 0                                            # 已经写了多少帧
    last = None                                        # 上一帧：没人声的空档就停在这一帧（不要黑屏，出镜框那时候还在画面里）
    for clip in CLIPS:
        ps = [p for p in tl if p["clip"] == clip]
        if not ps:
            continue
        wins = []
        for p in ps:
            n = round((p["out_out"] - p["out_in"]) * FQ)
            s0 = int(round(p["src_in"] * FQ))
            wins.append((s0, s0 + n - 1, round(p["out_in"] * FQ), n))
        expr = "+".join("between(n,%d,%d)" % (a, b) for a, b, _, _ in wins)
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-nostdin", "-i", str(FACE / "proxy" / ("%s.mp4" % clip)), "-an",
                                "-vf", "select='%s',scale=%d:%d:flags=area" % (expr, w, h), "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=fb * 8)
        for a, b, o, n in wins:
            first = None
            if cur < o:
                if last is None:                       # 最开头的空档（开场快切）：用这一段的第一帧
                    first = dec.stdout.read(fb)
                    last = first if len(first) == fb else black
                while cur < o:
                    enc.stdin.write(last)
                    cur += 1
            for k in range(n):
                buf = first if (k == 0 and first is not None) else dec.stdout.read(fb)
                if len(buf) < fb:                      # 素材比预期短：补最后一帧（不该发生）
                    buf = last if last is not None else black
                enc.stdin.write(buf)
                last = buf
                cur += 1
        dec.stdout.close()
        dec.wait()
    enc.stdin.close()
    enc.wait()
    return cur


def find_phrase(clip: str, text: str, after: float = 0.0):
    """在某条出镜素材的 ASR 逐词时间里找一句话，返回这句话第一个字的源时间（秒）。找不到返回 None。"""
    import re
    toks = []
    for seg in asr_segments()[clip]:
        for w in seg["words"]:
            toks.append(w)
    chars, idx = [], []
    for i, w in enumerate(toks):
        for ch in re.sub(r"[\s,，。.!！?？、；;：:“”\"'《》]", "", w["w"]):
            chars.append(ch)
            idx.append(i)
    flat = "".join(chars)
    key = re.sub(r"[\s,，。.!！?？、；;：:“”\"'《》]", "", text)
    pos = 0
    while True:
        j = flat.find(key, pos)
        if j < 0:
            return None
        tok = toks[idx[j]]
        if tok["s"] >= after - 1e-6:
            return tok["s"]
        pos = j + 1


def asr_segments():
    out = {}
    for c in CLIPS:
        out[c] = json.loads((FACE / "asr" / f"{c}.json").read_text(encoding="utf-8"))["segments"]
    return out


if __name__ == "__main__":
    tl = timeline()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "show":
        print("成片口播共 %.1f 秒（%d 个片段）" % (total(tl), len(tl)))
        for c, segs in asr_segments().items():
            print("== %s" % c)
            for s in segs:
                a, b = out_time(tl, c, s["start"] + 0.05), out_time(tl, c, s["end"] - 0.05)
                kept = any(p["clip"] == c and p["src_in"] - 0.3 <= s["start"] and s["end"] <= p["src_out"] + 0.3 for p in tl)
                print("%s %6.1f–%6.1f → %6.1f–%6.1f  %s" % (" " if kept else "×", s["start"], s["end"], a, b, s["text"].strip()[:70]))
    elif cmd == "face":
        n = face_timeline(tl, HERE / "face_tl.mp4")
        print("face_tl.mp4", n, "帧", n / FQ, "秒")
    elif cmd == "audio":
        render_audio(tl, HERE / "人声.wav")
        print("人声.wav", total(tl))
