# -*- coding: utf-8 -*-
"""按 cues.json 剪出口播：去口癖、去重录、去长停顿，得到干净的人声和对应的出镜画面（声音和画面在同一帧上切）。

cues.json（make_cues.py 生成）：按成片顺序排的字幕条
  {"pid", "clip", "s", "e", "zh", "en", "skip": [[s, e], ...]}   s / e 是原录像里的秒数，skip 是条内要剪掉的口癖
规则：
  - 每块前后多留 PRE / POST 秒；同一段录像里前后两条间隔小于 JOIN 就连着不切（保留自然停顿）；
  - 不连着的两条之间插入停顿：同一段 GAP_LINE，换段 GAP_PARA；
  - 块里面超过 SIL_MIN 秒的静音（能量低于这段录像说话电平 30 dB）自动缩成 SIL_KEEP 秒；
  - 字幕条带 hold=(秒, 录像, 起点)：这条念完后插入一段不说话的镜头（声音也用那段的环境声），作品展示时让片段原声出来。
输出（edit/）：narration.wav（48 kHz 立体声）、facecam.mp4（1280×720 30 fps 无声）、edit.json（每条字幕、每段在成片里的时间）。
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
FPS, SR = 30, 48000
PRE, POST = 0.06, 0.10
GAP_LINE, GAP_PARA = 0.12, 0.30
JOIN = 0.35
SIL_MIN, SIL_KEEP = 0.45, 0.22
FADE = 0.012


def read_wav(p):
    with wave.open(str(p)) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, w.getnchannels()).astype(np.float32) / 32768


def fr(x):
    return int(round(x * FPS))


def silences(a, f0, f1):
    """[f0, f1) 帧范围里超过 SIL_MIN 的静音段（帧号）。"""
    hop = SR // FPS                                   # 一帧一个能量值
    seg = a[f0 * hop: f1 * hop].mean(axis=1)
    n = len(seg) // hop
    if n == 0:
        return []
    rms = np.sqrt((seg[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    return db


def main():
    cues = json.loads((HERE / "cues.json").read_text(encoding="utf-8"))
    audio, level = {}, {}
    for c in cues:
        if c["clip"] not in audio:
            a = read_wav(HERE / "audio" / f"{c['clip']}.wav")
            audio[c["clip"]] = a
            hop = SR // FPS
            m = a.mean(axis=1)
            n = len(m) // hop
            db = 20 * np.log10(np.sqrt((m[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12))
            level[c["clip"]] = np.percentile(db, 95)      # 这段录像的说话电平
    # 1) 每条字幕的源区间（去掉 skip），按帧取整；前后紧挨着的并成一块
    pieces = []
    for i, c in enumerate(cues):
        rngs = [[c["s"] - PRE, c["e"] + POST]]
        for a0, b0 in sorted(c.get("skip", [])):
            nr = []
            for r0, r1 in rngs:
                if b0 <= r0 or a0 >= r1:
                    nr.append([r0, r1])
                else:
                    if a0 > r0:
                        nr.append([r0, a0])
                    if b0 < r1:
                        nr.append([b0, r1])
            rngs = nr
        for j, (r0, r1) in enumerate(rngs):
            f0, f1 = max(0, fr(r0)), fr(r1)
            if f1 - f0 < 2:
                continue
            last = pieces[-1] if pieces else None
            if last and not last.get("hold") and last["clip"] == c["clip"] and j == 0 and not c.get("cut") and -1 <= f0 - last["f1"] <= fr(JOIN):
                last["f1"] = max(last["f1"], f1)
                last["cues"].append(i)
                continue
            if last and not last.get("hold"):
                last["gap"] = fr(GAP_LINE if cues[last["cues"][-1]]["pid"] == c["pid"] else GAP_PARA)
            pieces.append({"clip": c["clip"], "f0": f0, "f1": f1, "gap": 0, "cues": [i]})
        if c.get("hold"):
            hd, hc, hs = c["hold"]
            pieces[-1]["gap"] = 0
            pieces.append({"clip": hc, "f0": fr(hs), "f1": fr(hs + hd), "gap": 0, "cues": [], "hold": i})
    # 2) 块里的长静音缩短：把一块拆成几小块（中间不插停顿）
    segs, cut_sil = [], 0
    for p in pieces:
        if "hold" in p:                                     # 停顿镜头整段保留
            segs.append({"clip": p["clip"], "f0": p["f0"], "f1": p["f1"], "gap": p["gap"], "cues": [], "hold": p["hold"]})
            continue
        db = silences(audio[p["clip"]], p["f0"], p["f1"])
        quiet = db < level[p["clip"]] - 30
        keep_ranges, k, n = [], 0, len(quiet)
        start = 0
        while k < n:
            if quiet[k]:
                j = k
                while j < n and quiet[j]:
                    j += 1
                if (j - k) / FPS > SIL_MIN and k > 0 and j < n:
                    half = fr(SIL_KEEP / 2)
                    keep_ranges.append((start, k + half))
                    start = j - half
                    cut_sil += (j - k - 2 * half)
                k = j
            else:
                k += 1
        keep_ranges.append((start, p["f1"] - p["f0"]))
        for m, (a0, b0) in enumerate(keep_ranges):
            segs.append({"clip": p["clip"], "f0": p["f0"] + a0, "f1": p["f0"] + b0,
                         "gap": p["gap"] if m == len(keep_ranges) - 1 else 0, "cues": p["cues"]})
    # 3) 拼人声、记下每小块在成片里的起点
    out, t = [], 0
    for sgm in segs:
        a = audio[sgm["clip"]]
        hop = SR // FPS
        seg = a[sgm["f0"] * hop: sgm["f1"] * hop].copy()
        nf = int(FADE * SR)
        if len(seg) > 2 * nf:
            seg[:nf] *= np.linspace(0, 1, nf)[:, None]
            seg[-nf:] *= np.linspace(1, 0, nf)[:, None]
        sgm["out_f0"] = t
        out.append(seg)
        t += sgm["f1"] - sgm["f0"]
        if sgm["gap"]:
            out.append(np.zeros((sgm["gap"] * hop, 2), dtype=np.float32))
            t += sgm["gap"]
    total_f = t
    (HERE / "edit").mkdir(exist_ok=True)
    y = np.concatenate(out)
    with wave.open(str(HERE / "edit" / "narration.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    # 4) 每条字幕在成片里的起止：落在哪几小块里就按那几小块换算
    info_cues = []
    for i, c in enumerate(cues):
        s_out, e_out = None, None
        for sgm in segs:
            if i not in sgm["cues"]:
                continue
            a0, b0 = sgm["f0"] / FPS, sgm["f1"] / FPS
            if b0 <= c["s"] or a0 >= c["e"]:
                continue
            base = sgm["out_f0"] / FPS - a0
            s_here = base + max(c["s"], a0)
            e_here = base + min(c["e"], b0)
            s_out = s_here if s_out is None else min(s_out, s_here)
            e_out = e_here if e_out is None else max(e_out, e_here)
        info_cues.append(dict(c, out_s=round(s_out, 3), out_e=round(e_out, 3)))
    # 5) 出镜画面：同样的剪法；插入停顿的地方源画面接着往后放（不出声）
    lst = HERE / "edit" / "_segs"
    lst.mkdir(exist_ok=True)
    names = []
    for k, sgm in enumerate(segs):
        nf = sgm["f1"] - sgm["f0"] + sgm["gap"]
        name = lst / f"s{k:04d}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sgm['f0'] / FPS:.4f}", "-i", str(HERE / "proxy" / f"{sgm['clip']}.mp4"),
                        "-frames:v", str(nf), "-an", "-vf", "fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                        "-pix_fmt", "yuv420p", str(name)], check=True)
        names.append(name)
    (lst / "list.txt").write_text("".join(f"file '{n.name}'\n" for n in names), encoding="utf-8")
    # 按帧重新编时间戳：直接 -c copy 拼接时每段的时长会多出一点，时间戳有空档（按时间抽帧会多出几十帧，口型越往后越慢）
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst / "list.txt"),
                    "-vf", f"setpts=N/{FPS}/TB", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "16", "-pix_fmt", "yuv420p", str(HERE / "edit" / "facecam.mp4")], check=True)
    paras = {}
    for c in info_cues:
        p = paras.setdefault(c["pid"], {"pid": c["pid"], "start": c["out_s"], "end": c["out_e"]})
        p["start"], p["end"] = min(p["start"], c["out_s"]), max(p["end"], c["out_e"])
    info = {"fps": FPS, "total": round(total_f / FPS, 3), "pieces": len(pieces),
            "segments": [{"clip": g["clip"], "src_s": round(g["f0"] / FPS, 3), "src_e": round(g["f1"] / FPS, 3), "out_s": round(g["out_f0"] / FPS, 3), "gap": round(g["gap"] / FPS, 3), **({"hold": g["hold"]} if "hold" in g else {})} for g in segs],
            "holds": [{"after": g["hold"], "out_s": round(g["out_f0"] / FPS, 3), "out_e": round((g["out_f0"] + g["f1"] - g["f0"]) / FPS, 3)} for g in segs if "hold" in g],
            "silence_cut": round(cut_sil / FPS, 2), "cues": info_cues, "paras": list(paras.values())}
    (HERE / "edit" / "edit.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    src = sum(c["e"] - c["s"] for c in cues)
    print(f"narration {total_f / FPS:.1f}s  ({len(pieces)} pieces → {len(segs)} segments, long pauses cut {cut_sil / FPS:.1f}s, cue spans {src:.1f}s)")


if __name__ == "__main__":
    main()
