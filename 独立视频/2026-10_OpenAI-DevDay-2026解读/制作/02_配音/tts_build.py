# -*- coding: utf-8 -*-
"""配音（Fish Audio 网页版，声音「赛马娘（曼波欧耶版）」，模型见 tts/model_used.txt，音频控制默认；一批一次生成两个版本）→ 按句切开、挑版本、拼成一条口播。
照《白宫超级智能协定》的 tts_build.py 改的：这里每句都带批次（make_lines.py 按台本的 "batch" 写进 lines.json），不再有“主批”。

  python tts_build.py

输入：tts/lines.json（每句：id / zh / say）、tts/raw/<批>_v1.mp3、<批>_v2.mp3、asr/<批>_v1.json、<批>_v2.json（asr.py 逐词识别）。
输出：edit/tts_narration.wav（48 kHz 立体声）、edit/tts_edit.json（每句：s/e = 有声音的起止，n0/n1 = 这句在口播里的切点，句与句首尾相接）。

挑版本：默认 v1；CHOICE 里写哪句用 v2（逐句对过识别结果之后定）。
切句：按逐词时间把原文和识别结果对上，相邻两句之间在最长的静音中点切一刀，停顿就是原版本里的自然停顿；换版本处两边各留 0.18 s 以内的静音。

多批：lines.json 里某句带 "batch": "I" 就是另一次生成（例：竖屏片段的两句同传，S2 Pro 单独生成的 I_v1.mp3 / I_v2.mp3 + asr/I_v1.json …）；
没写 batch 的都是主批（BATCH，默认 N，用 --batch G 指定）。各批按句子在 lines.json 里的先后顺序首尾相接拼进同一条口播。
"""
import difflib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
BATCH = "A"
CHOICE = {}          # {"V1-N12": "v2", …}（edit/choice.json 里也可以写）
CUT_FIX = {}         # {("v1", "V1-N30"): 秒}：自动切点不对的地方手工指定（后一句的起点）
# {(批, 版本, 句号): 秒}：只把这一句的起点往后挪（前一句的止点不动），中间那段不要了（例：某句开头被多念了一遍）。
START_FIX = {}


def norm_chars(s):
    return [c for c in s.lower() if re.match(r"\w", c) and c != "_"]


def load_audio(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def env_db(a, hop=0.01):
    h = int(SR * hop)
    m = a.mean(1)
    n = len(m) // h
    return 20 * np.log10(np.sqrt((m[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)


def char_times(asr):
    out = []
    for s in asr["segments"]:
        for w in s["words"]:
            cs = norm_chars(w["w"])
            if not cs:
                continue
            d = (w["e"] - w["s"]) / len(cs)
            out += [(c, w["s"] + k * d, w["s"] + (k + 1) * d) for k, c in enumerate(cs)]
    return out


def align(lines, asr):
    """每句在这个版本里的 (起, 止)：原文和识别结果按字对齐。"""
    ref, owner = [], []
    for i, l in enumerate(lines):
        cs = norm_chars(l["say"])
        ref += cs
        owner += [i] * len(cs)
    hyp = char_times(asr)
    sm = difflib.SequenceMatcher(None, ref, [c for c, _, _ in hyp], autojunk=False)
    t = [None] * len(ref)
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op in ("equal", "replace") and b2 > b1:
            for k in range(a1, a2):
                j = b1 + int((k - a1) * (b2 - b1) / max(1, a2 - a1))
                t[k] = (hyp[j][1], hyp[j][2])
    spans = []
    for i in range(len(lines)):
        ks = [k for k in range(len(ref)) if owner[k] == i and t[k]]
        spans.append((t[ks[0]][0], t[ks[-1]][1]) if ks else None)
    return spans


def cuts(db, spans, total):
    """相邻两句之间切一刀：在“上一句识别止 − 0.15 s … 下一句识别起 + 0.15 s”里找最长的一段静音（< -50 dB）取中点，没有静音就取电平最低的那一帧。"""
    hop = 0.01
    b = [0.0]
    for i in range(len(spans) - 1):
        lo = int(max(b[-1] + 0.2, spans[i][1] - 0.15) / hop)
        hi = int(max(lo + 2, (spans[i + 1][0] + 0.15) / hop))
        w = db[lo:hi]
        q = w < -50
        best, k = None, 0
        while k < len(w):
            if q[k]:
                j = k
                while j < len(w) and q[j]:
                    j += 1
                if best is None or j - k > best[1] - best[0]:
                    best = (k, j)
                k = j
            else:
                k += 1
        c = (lo + (best[0] + best[1]) / 2) if best else lo + int(np.argmin(w))
        b.append(c * hop)
    b.append(total)
    return [(b[i], b[i + 1]) for i in range(len(spans))]


def voiced(db, s, e):
    """这一段里真正有声音的起止（> -45 dB），给字幕用。"""
    hop = 0.01
    i0, i1 = int(s / hop), int(e / hop)
    idx = np.where(db[i0:i1] > -45)[0]
    return (s, e) if len(idx) == 0 else ((i0 + idx[0]) * hop, (i0 + idx[-1] + 1) * hop)


def load_take(batch, v, lines_b):
    """一个批次、一个版本：音频 + 电平 + 每句的切点（按这个批次的句子表）。"""
    a = load_audio(HERE / "tts" / "raw" / f"{batch}_{v}.mp3")
    asr = json.loads((HERE / "asr" / f"{batch}_{v}.json").read_text(encoding="utf-8"))
    db = env_db(a)
    spans = align(lines_b, asr)
    bad = [lines_b[i]["id"] for i, sp in enumerate(spans) if sp is None]
    assert not bad, f"{batch}_{v} 对不上的句子：{bad}"
    cs = cuts(db, spans, len(a) / SR)
    for i, l in enumerate(lines_b):
        if (v, l["id"]) in CUT_FIX:
            x = CUT_FIX[(v, l["id"])]
            cs[i - 1], cs[i] = (cs[i - 1][0], x), (x, cs[i][1])
        if (batch, v, l["id"]) in START_FIX:
            cs[i] = (START_FIX[(batch, v, l["id"])], cs[i][1])
    return a, db, cs


def main():
    global BATCH
    if "--batch" in sys.argv:
        BATCH = sys.argv[sys.argv.index("--batch") + 1]
    lines = json.loads((HERE / "tts" / "lines.json").read_text(encoding="utf-8"))
    cf = HERE / "edit" / "choice.json"
    if cf.exists():
        CHOICE.update(json.loads(cf.read_text(encoding="utf-8")))
    groups, pos = {}, {}                 # 批次 → 这个批次的句子；句号 → (批次, 在批次里的序号)
    for l in lines:
        b = l.get("batch", BATCH)
        groups.setdefault(b, []).append(l)
        pos[l["id"]] = (b, len(groups[b]) - 1)
    takes = {}                           # (批次, 版本) → (音频, 电平, 切点)
    for b, lb in groups.items():
        for v in ("v1", "v2"):
            if not (HERE / "tts" / "raw" / f"{b}_{v}.mp3").exists():     # 只拿到一个版本时，v2 当 v1 用
                takes[(b, v)] = takes[(b, "v1")]
                continue
            takes[(b, v)] = load_take(b, v, lb)
    tk = lambda i: (pos[lines[i]["id"]][0], CHOICE.get(lines[i]["id"], "v1"))   # 第 i 句用的 (批次, 版本)
    out, segs, t = [], [], 0.0
    fade = int(0.005 * SR)
    for i, l in enumerate(lines):
        b, ib = pos[l["id"]]
        v = CHOICE.get(l["id"], "v1")
        a, db, cs = takes[(b, v)]
        s, e = cs[ib]
        if i and tk(i - 1) != (b, v):
            vs, _ = voiced(db, s, e)
            s = max(s, vs - 0.18)
        if i + 1 < len(lines) and tk(i + 1) != (b, v):
            _, ve = voiced(db, s, e)
            e = min(e, ve + 0.18)
        seg = a[int(s * SR): int(e * SR)].copy()
        r = np.linspace(0, 1, fade)[:, None]
        seg[:fade] *= r
        seg[-fade:] *= r[::-1]
        vs, ve = voiced(db, s, e)
        segs.append({"id": l["id"], "zh": l["zh"], "take": f"{b}_{v}" if b != BATCH else v, "src": [round(s, 3), round(e, 3)],
                     "n0": round(t, 3), "n1": round(t + e - s, 3), "s": round(t + vs - s, 3), "e": round(t + ve - s, 3)})
        out.append(seg)
        t += e - s
    y = np.concatenate(out)
    (HERE / "edit").mkdir(exist_ok=True)
    with wave.open(str(HERE / "edit" / "tts_narration.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    (HERE / "edit" / "tts_edit.json").write_text(json.dumps({"total": round(len(y) / SR, 3), "lines": segs}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"tts_narration.wav {len(y) / SR:.2f} s，{len(segs)} 句，批次 {'、'.join(groups)}；用 v2 的：" + (", ".join(k for k, v in CHOICE.items() if v == "v2") or "无"))
    for x in segs:
        print(f"  {x['id']} {x['take']} 源 {x['src'][0]:6.2f}–{x['src'][1]:6.2f}  → {x['s']:6.2f}–{x['e']:6.2f}  {x['zh']}")


if __name__ == "__main__":
    main()
