# -*- coding: utf-8 -*-
"""克隆声音配音（Fish Audio 网页版，声音「悠一」，模型 S1，音频控制默认；2026-10-01 13:48 一次生成两个版本）→ 按句切开、挑版本、拼成一条口播。

  python tts_build.py

输入：tts/lines.json（31 句：R01–R22 = 剪好的录屏口播原话，M01–M09 = 手机演示画外音；say = 念的文本，数字写成汉字）、
      tts/raw/R_v1.mp3、R_v2.mp3、asr/R_v1.json、asr/R_v2.json（asr.py 逐词识别）。
输出：edit/tts_narration.wav（48 kHz 立体声）、edit/tts_edit.json（每句在口播里的起止 s/e、用的版本）。

挑版本（逐句对过识别结果，可疑处用“短窗 + 原文当提示词”再识别确认）：
- 默认 v1；R02 用 v2（v1 在“搜一下”后面多念了个“看”）；
- R03 不能用 v2（v2 在句首多了“更早”）；M08、M09 用 v2（v1 的“没绑卡”听着像“没网卡”、“扣不上”像“够不上”）。
切句：按逐词时间对上原文，相邻两句之间在最长的静音中点切一刀（句与句首尾相接，停顿就是原版本里的自然停顿）；换版本处两边各留 0.18 s 以内的静音。
"""
import difflib
import json
import re
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
CHOICE = {"R02": "v2", "M08": "v2", "M09": "v2"}
# 自动切点不对的地方手工指定（版本, 后一句编号）→ 秒：v1 第一遍识别漏了 M05 末尾的“就订阅好了”（56.00–56.72），切点落到了它前面
CUT_FIX = {("v1", "M06"): 56.89}


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
    """识别结果 → 每个字（规范化后）的 (字, 起, 止)。一个词里的字平均分时间。"""
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
    """每句在这个版本里的 (起, 止)：原文和识别结果按字对齐（数字“124.99”对“一百二十四点九九”这种按比例对）。"""
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
    """相邻两句之间切一刀：在“上一句识别止 − 0.15 s … 下一句识别起 + 0.15 s”里找最长的一段静音（< -50 dB）取中点，
    没有静音就取电平最低的那一帧。返回每句的 [起, 止]（首句从 0 起，末句到音频结束），句与句首尾相接、不重叠。"""
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


def main():
    lines = json.loads((HERE / "tts" / "lines.json").read_text(encoding="utf-8"))
    takes = {}
    for v in ("v1", "v2"):
        a = load_audio(HERE / "tts" / "raw" / f"R_{v}.mp3")
        asr = json.loads((HERE / "asr" / f"R_{v}.json").read_text(encoding="utf-8"))
        db = env_db(a)
        cs = cuts(db, align(lines, asr), len(a) / SR)
        for i, l in enumerate(lines):
            if (v, l["id"]) in CUT_FIX:
                x = CUT_FIX[(v, l["id"])]
                cs[i - 1], cs[i] = (cs[i - 1][0], x), (x, cs[i][1])
        takes[v] = (a, db, cs)
    out, segs, t = [], [], 0.0
    fade = int(0.005 * SR)
    for i, l in enumerate(lines):
        v = CHOICE.get(l["id"], "v1")
        a, db, cs = takes[v]
        s, e = cs[i]
        # 换版本的地方：两边各自的静音不一定一样长，前后各留到 0.18 s 以内
        if i and CHOICE.get(lines[i - 1]["id"], "v1") != v:
            vs, _ = voiced(db, s, e)
            s = max(s, vs - 0.18)
        if i + 1 < len(lines) and CHOICE.get(lines[i + 1]["id"], "v1") != v:
            _, ve = voiced(db, s, e)
            e = min(e, ve + 0.18)
        seg = a[int(s * SR): int(e * SR)].copy()
        r = np.linspace(0, 1, fade)[:, None]
        seg[:fade] *= r
        seg[-fade:] *= r[::-1]
        vs, ve = voiced(db, s, e)
        segs.append({"id": l["id"], "zh": l["zh"], "take": v, "src": [round(s, 3), round(e, 3)],
                     "s": round(t + vs - s, 3), "e": round(t + ve - s, 3)})
        out.append(seg)
        t += e - s
    # 地区提醒（用户 2026-10-01 定“放”；14:55 另生成一批 W_v1 / W_v2，tts/lines_w.json）：
    # 两个版本都多念了音节（v1 在“地区，”后 3.40–3.74、两版在“礼品卡”前），按停顿手工切，三句都用 v1。
    # W03 的起点：第一次用 7.45，成片复核时（qa_mix.py）听成“在礼品卡”——多余音节的尾巴还在；
    # 7.45 / 7.465 / 7.475 各用 4 种解码设置识别：只有 7.475 四次都是干净的“礼品卡买了也不能退”（7.465 会切到“礼”的开头）。
    wl = {l["id"]: l for l in json.loads((HERE / "tts" / "lines_w.json").read_text(encoding="utf-8"))}
    W = [("W01", 0.20, 3.38, 0.30), ("W02", 3.98, 6.94, 0.35), ("W03", 7.475, 10.0, 0.0)]
    wa = load_audio(HERE / "tts" / "raw" / "W_v1.mp3")
    wdb = env_db(wa)
    gap0 = 0.5
    out.append(np.zeros((int(gap0 * SR), 2), np.float32))
    t += gap0
    for wid, s, e, gap in W:
        seg = wa[int(s * SR): int(e * SR)].copy()
        fi = int(0.02 * SR)
        seg[:fi] *= np.linspace(0, 1, fi)[:, None]
        seg[-fade:] *= np.linspace(1, 0, fade)[:, None]
        vs, ve = voiced(wdb, s, e)
        segs.append({"id": wid, "zh": wl[wid]["zh"], "take": "W_v1", "src": [s, e], "s": round(t + vs - s, 3), "e": round(t + ve - s, 3)})
        out += [seg, np.zeros((int(gap * SR), 2), np.float32)]
        t += e - s + gap
    y = np.concatenate(out)
    import wave
    (HERE / "edit").mkdir(exist_ok=True)
    with wave.open(str(HERE / "edit" / "tts_narration.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    (HERE / "edit" / "tts_edit.json").write_text(json.dumps({"total": round(len(y) / SR, 3), "lines": segs}, ensure_ascii=False, indent=1), encoding="utf-8")
    r_end = next(x["e"] for x in segs if x["id"] == "R22")
    print(f"tts_narration.wav {len(y) / SR:.2f} s：R01–R22 到 {r_end:.2f} s，M01–M09 {len(y) / SR - r_end:.2f} s；版本 " +
          ", ".join(f"{x['id']}={x['take']}" for x in segs if x["take"] != "v1"))
    for x in segs:
        print(f"  {x['id']} {x['take']} 源 {x['src'][0]:6.2f}–{x['src'][1]:6.2f}  → {x['s']:6.2f}–{x['e']:6.2f}  {x['zh']}")


if __name__ == "__main__":
    main()
