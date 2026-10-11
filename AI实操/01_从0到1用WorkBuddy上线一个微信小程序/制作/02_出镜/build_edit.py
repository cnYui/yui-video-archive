# -*- coding: utf-8 -*-
"""按 cues.json 剪成片的时间轴：人声、录屏、出镜三条在同一帧上切。

规则（每一段 seg 是同一次录制的连续一截，主时间 = 录屏秒数；0162 单录的口播主时间 = 出镜秒数）：
  1. 每条字幕的声音区间（去掉 skip）按能量检测收紧 / 放宽到真正说话的地方，前后多留 PRE / POST；
     条内超过 SPLIT 秒的停顿拆开，交给第 2 条处理。
  2. 两块说话之间的空档（主时间）：
     - ≤ KEEP 秒：原样保留（1 倍速，带原声）；
     - 更长：先去掉“画面静止”的部分（录屏 10 fps 相邻帧几乎没变，只有光标在动也算静止），
       剩下“画面在动”的部分（打字、点按钮、AI 在出字）整体加速，压到 target(秒) 以内，静音；
       出镜跟着同样加速（快进时人也是快进的）。没有录屏的段（版式 A）空档直接剪成 PAUSE 秒（取最安静的一截）。
  3. 段尾写 ("to", 主时间) 的：一直放到那里，按第 2 条压缩（AI 生成的长时间等待 → 快进）。
  4. takes.BLACKOUT 里的录屏时间（误开微信）：空档里的直接剪掉；说话时落进去的部分，录屏画面定格在边缘的干净帧上。
输出 edit/edit.json（每个成片片段的来源和倍速、每条字幕在成片里的起止）、edit/narration.wav（48 kHz 立体声，已按来源统一电平）。
"""
import json
import wave
from pathlib import Path

import numpy as np

from takes import BLACKOUT, CAM_DUR, FPS, SCR_DUR, SRC_TAKE, VO_DUR, cam_at, has_screen, to_master

HERE = Path(__file__).resolve().parent
ACT = HERE.parents[0] / "01_录屏" / "activity"
SR = 48000
PRE, POST = 0.10, 0.16          # 说话前后多留
EXT_S, EXT_E = 1.20, 0.80       # 字幕条边界最多往外找这么远，放宽到说话真正开始 / 结束的地方（不越过硬边界）
SPLIT = 0.60                    # 条内停顿超过这个就拆开
LEAD_GAP = 0.80                 # 句首前面隔着这么近的说话块也算这一条的（Whisper 给句首字的时间常晚半秒）
JOIN = 0.25                     # 两块说话间隔小于这个就并成一块
KEEP = 0.65                     # 空档 ≤ 这个原样保留
PAUSE = 0.30                    # 没有录屏的段，空档剪成这么长
STATIC_AREA = 0.0012            # 10 fps 相邻帧变化面积小于这个算“静止”（光标移动约 0.001）
STATIC_MIN = 0.5                # 连续静止超过这么久才剪
TARGET_LEVEL = -20.0            # 各来源说话电平统一到这里（10 ms 能量的 95 分位，dBFS）


def target(a):
    """“画面在动”的 a 秒压到多少秒。"""
    if a <= 1.0:
        return a
    if a <= 12:
        return 1.0 + 0.30 * (a - 1.0)
    return min(4.3 + 0.035 * (a - 12), 9.0)


# ─────────────────────────────── 音频、能量
_AUD, _ENV = {}, {}


def audio(src):
    if src not in _AUD:
        with wave.open(str(HERE / "audio" / f"{src}.wav")) as w:
            assert w.getframerate() == SR
            a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(np.float32) / 32768
        _AUD[src] = a
    return _AUD[src]


def env(src):
    """10 ms 一格的能量（dBFS）、说话门限、说话电平。"""
    if src not in _ENV:
        a = audio(src).mean(1)
        hop = SR // 100
        n = len(a) // hop
        db = 20 * np.log10(np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
        lev = float(np.percentile(db, 95))
        floor = float(max(np.percentile(db, 10), -90))
        thr = max(lev - 32, floor + 9)
        _ENV[src] = (db, thr, lev)
    return _ENV[src]


def voiced(src, t0, t1):
    db, thr, _ = env(src)
    a, b = max(0, int(t0 * 100)), min(len(db), int(np.ceil(t1 * 100)))
    return db[a:b] > thr, a


def tighten(src, s, e, lo, hi):
    """把 [s, e] 收紧 / 放宽到真正说话的地方（不超出硬边界 [lo, hi]）；返回拆开后的若干块 [(s, e)]。
    Whisper 给停顿后第一个字的时间常常偏晚 0.2–0.5 s：和字幕条连着的说话块整块保留（往前最多找 EXT_S 秒）。"""
    v, base = voiced(src, max(lo, s - EXT_S), min(hi, e + EXT_E))
    idx = np.where(v)[0]
    if len(idx) == 0:
        return []
    t = (idx + base) / 100.0
    # 起点：s 之前如果还连着在说话，往前放宽；s 之后才开始说的，收紧
    blocks, cur = [], [t[0], t[0] + 0.01]
    for x in t[1:]:
        if x - cur[1] > SPLIT:
            blocks.append(cur)
            cur = [x, x + 0.01]
        else:
            cur[1] = x + 0.01
    blocks.append(cur)
    keep = [k for k, (a, b) in enumerate(blocks) if not (b < s - 0.05 or a > e + 0.05)]
    if not keep:
        return []
    # 句首轻声的字（“所以”“如果”“你可以”）常常和后面隔着半秒多：前一块离第一块 ≤ LEAD_GAP 也算进来
    k0 = keep[0]
    while k0 > 0 and blocks[k0][0] - blocks[k0 - 1][1] <= LEAD_GAP and blocks[k0 - 1][0] >= lo:
        k0 -= 1
    keep = list(range(k0, keep[-1] + 1))
    out = []
    for k in keep:
        a, b = blocks[k]
        out.append((max(lo, a - PRE), min(hi, b + POST)))
    return out


def snap(src, t, w=0.10):
    """t 附近 ±w 秒里能量最低的那一格（剪口误时剪在字缝里）。"""
    db, _, _ = env(src)
    a, b = max(0, int((t - w) * 100)), min(len(db), int((t + w) * 100) + 1)
    if b <= a:
        return t
    return (a + int(np.argmin(db[a:b]))) / 100.0 + 0.005


def quietest(src, t0, t1, d):
    """[t0, t1] 里最安静的 d 秒的起点。"""
    db, _, _ = env(src)
    a, b = int(t0 * 100), int(t1 * 100)
    k = int(d * 100)
    if b - a <= k:
        return t0
    w = np.convolve(db[a:b], np.ones(k) / k, mode="valid")
    return (a + int(np.argmin(w))) / 100.0


# ─────────────────────────────── 录屏活动度
_ACTV = {}


def activity(take):
    if take not in _ACTV:
        d = json.loads((ACT / f"{take}.json").read_text(encoding="utf-8"))
        _ACTV[take] = np.array(d["area"])
    return _ACTV[take]


def active_runs(take, m0, m1, static_min=STATIC_MIN):
    """[m0, m1] 里“画面在动”的区间（去掉连续静止 ≥ static_min 的部分，以及 BLACKOUT）。"""
    area = activity(take)
    a, b = int(max(0, m0) * 10), int(min(SCR_DUR[take], m1) * 10)
    runs = []
    if b > a:
        mov = area[a:b] > STATIC_AREA
        # 静止段短于 STATIC_MIN 的当作在动（保持连贯）
        k = 0
        n = len(mov)
        st = np.zeros(n, bool)
        while k < n:
            if not mov[k]:
                j = k
                while j < n and not mov[j]:
                    j += 1
                if (j - k) / 10 >= static_min:
                    st[k:j] = True
                k = j
            else:
                k += 1
        k = 0
        while k < n:
            if not st[k]:
                j = k
                while j < n and not st[j]:
                    j += 1
                runs.append([(a + k) / 10, (a + j) / 10])
                k = j
            else:
                k += 1
    # 头尾补齐到 m0 / m1（在录屏范围外的部分不算）
    if runs:
        runs[0][0] = max(runs[0][0], m0)
        runs[-1][1] = min(runs[-1][1], m1)
    runs = [r for r in runs if r[1] - r[0] > 0.05]
    return cut_blackout(take, runs)


def cut_blackout(take, runs, extra=()):
    out = []
    for r0, r1 in runs:
        pieces = [[r0, r1]]
        for b0, b1 in list(BLACKOUT.get(take, [])) + list(extra):
            nxt = []
            for p0, p1 in pieces:
                if p1 <= b0 or p0 >= b1:
                    nxt.append([p0, p1])
                else:
                    if p0 < b0:
                        nxt.append([p0, b0])
                    if p1 > b1:
                        nxt.append([b1, p1])
            pieces = nxt
        out += [p for p in pieces if p[1] - p[0] > 0.05]
    return out


# ─────────────────────────────── 片段
CLIPS = []
REMOVED = {}                             # 段 → [(主时间起, 止)]：字幕条里 skip 掉的口误（空档里不能再把它放出来）


def add_clip(seg_i, seg, kind, m0, dur, speed=1.0, aud=None, cues=(), cam_m=None):
    """m0：主时间起点；dur：成片里的时长（秒）；speed：主时间走多快。aud = (来源, 来源时间起点) 或 None（静音）。
    cam_m：出镜另取的主时间起点（默认和画面一样）。"""
    n = int(round(dur * FPS))
    if n <= 0:
        return
    CLIPS.append({"seg": seg_i, "take": seg["take"], "layout": seg["layout"], "chapter": seg["chapter"], "kind": kind,
                  "scr_freeze": seg.get("scr_freeze"),
                  "m0": round(m0, 4), "speed": round(speed, 4), "n": n, "aud": aud, "cues": list(cues),
                  "cam_m0": round(cam_m if cam_m is not None else m0, 4)})


def audio_src_at(take, m):
    """主时间 m 的声音来源：有出镜就用出镜的声音，没有就用录屏的。"""
    c = cam_at(take, m)
    if c:
        return c
    if has_screen(take):
        return take, m
    return None


def emit_gap(i, seg, m0, m1, cues_here):
    """两块说话之间的空档 [m0, m1]（主时间）。"""
    g = m1 - m0
    if g <= 1e-3:
        return
    take = seg["take"]
    screen = has_screen(take) and seg["layout"] == "B"
    if g <= KEEP:
        if any(r0 < m1 - 0.02 and r1 > m0 + 0.02 for r0, r1 in REMOVED.get(take, [])):
            return                       # 空档里是剪掉的口误：直接接上，不留这段声音
        src = audio_src_at(take, m0)
        if screen and any(b0 < m1 and b1 > m0 for b0, b1 in BLACKOUT.get(take, [])):
            add_clip(i, seg, "pause", m0, min(g, 0.2), aud=None, cues=cues_here)
            return
        add_clip(i, seg, "pause", m0, g, aud=src, cues=cues_here)
        return
    if not screen:
        # 没有录屏：剪成 PAUSE 秒，取最安静的一截（出镜和声音都用这截）
        src = audio_src_at(take, m0)
        if src:
            sid, st = src
            q = quietest(sid, st, st + g, PAUSE)
            add_clip(i, seg, "pause", m0 + (q - st), PAUSE, aud=(sid, q), cues=cues_here)
        else:
            add_clip(i, seg, "pause", m0, PAUSE, cues=cues_here)
        return
    # 长空档（AI 在生成）做成连贯的快进：只去掉 3 秒以上的静止，间隔很近的几截并起来
    runs = active_runs(take, m0, m1, STATIC_MIN if g <= 12 else 3.0)
    runs = cut_blackout(take, runs, REMOVED.get(take, []))       # 删掉的话所在的时间也不放（不做快进）
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < (0.3 if g <= 12 else 1.0) and not any(b0 < r[0] and b1 > merged[-1][1] for b0, b1 in BLACKOUT.get(take, [])):
            merged[-1][1] = r[1]
        else:
            merged.append(list(r))
    runs = merged
    a = sum(r1 - r0 for r0, r1 in runs)
    if a <= 0.05:
        add_clip(i, seg, "pause", m0, 0.25, aud=None, cues=cues_here)
        return
    t = target(a)
    sp = a / t
    if sp < 1.25:
        sp = 1.0
    for r0, r1 in runs:
        kind = "gap" if sp == 1.0 else "fast"
        aud = None
        if sp == 1.0:
            src = audio_src_at(take, r0)
            # 1 倍速的空档，原声里如果有人声（剪掉的口误）就静音
            if src and voiced(src[0], src[1], src[1] + (r1 - r0))[0].mean() < 0.15:
                aud = src
        add_clip(i, seg, kind, r0, (r1 - r0) / sp, speed=sp, aud=aud, cues=cues_here)


def main():
    data = json.loads((HERE / "cues.json").read_text(encoding="utf-8"))
    segs = data["segs"]
    all_cues = [q for sg in segs for q in sg["cues"]]
    cue_pieces = {}                       # cue id → 含有它的片段下标
    cue_ranges = {}                       # cue id → [(主时间起, 止)]
    for i, seg in enumerate(segs):
        take = seg["take"]
        pieces = []                       # (m0, m1, src, t0, cue_id)
        for q in seg["cues"]:
            src = q["src"]
            assert SRC_TAKE[src] == take, (q["id"], src, take)
            if q.get("drop"):                      # 删掉的整句：不进成片，空档里也不能再放出来
                REMOVED.setdefault(take, []).append((to_master(src, q["s"]), to_master(src, q["e"])))
                continue
            dur = CAM_DUR.get(src) or SCR_DUR.get(src) or VO_DUR.get(src)
            rngs = [[q["s"], q["e"]]]
            for sk in sorted(q["skip"]):
                a0, b0 = sk[0], sk[1]
                if len(sk) < 3:                   # 写了 "exact" 的剪点是试听确认过的，不再吸附
                    a0, b0 = snap(src, a0), snap(src, b0)
                REMOVED.setdefault(take, []).append((to_master(src, a0), to_master(src, b0)))
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
            got = []
            # 硬边界：同一来源的前一条结尾 / 后一条开头（别把别的句子、剪掉的口误带进来），也可以在字幕条里写 hard=(左, 右)
            same = [x for x in all_cues if x["src"] == src and x is not q]
            pv = max([x for x in same if x["e"] <= q["s"] + 0.05], key=lambda x: x["e"], default=None)
            nx = min([x for x in same if x["s"] >= q["e"] - 0.05], key=lambda x: x["s"], default=None)
            prev_e = pv["e"] if pv else 0.0
            next_s = nx["s"] if nx else dur
            # 邻句是删掉的整句（drop）：只放宽到两句之间的中点，免得把删掉的话带回来
            if pv and pv.get("drop"):
                prev_e = (pv["e"] + q["s"]) / 2
            if nx and nx.get("drop"):
                next_s = (q["e"] + nx["s"]) / 2
            hard_lo, hard_hi = q.get("hard", (None, None))
            hard_lo = max(prev_e, hard_lo if hard_lo is not None else 0.0)
            hard_hi = min(next_s, hard_hi if hard_hi is not None else dur)
            for k, (r0, r1) in enumerate(rngs):
                # 挨着 skip（剪掉的口误）的一边不往外放宽
                lo = r0 if (k > 0 or r0 > q["s"] + 1e-6) else max(hard_lo, r0 - EXT_S)
                hi = r1 if (k + 1 < len(rngs) or r1 < q["e"] - 1e-6) else min(hard_hi, r1 + EXT_E)
                if q.get("whole"):
                    got.append((max(lo, r0 - PRE), min(hi, r1 + POST), r0, r1))
                    continue
                for a, b in tighten(src, r0, r1, lo, hi):
                    got.append((a, b, max(a + PRE, r0), min(b - POST, r1)))
            if not got:
                print("!! 没检测到说话：", q["id"], q["zh"])
                got = [(q["s"], q["e"], q["s"], q["e"])]
            for a, b, sa, sb in got:
                m0, m1 = to_master(src, a), to_master(src, b)
                pieces.append([m0, m1, src, a, q["id"]])
                # 字幕的起止：真正说话的地方，但不越过手标的字缝（不和前后两条重叠）
                if sb > sa:
                    cue_ranges.setdefault(q["id"], []).append((to_master(src, sa), to_master(src, sb)))
        pieces.sort(key=lambda p: p[0])
        # 相邻块合并（同一来源、间隔小）
        merged = []
        for p in pieces:
            if merged and p[2] == merged[-1][2] and p[0] - merged[-1][1] < JOIN and abs((p[0] - merged[-1][0]) - (p[3] - merged[-1][3])) < 0.02:
                merged[-1][1] = max(merged[-1][1], p[1])
                merged[-1][4] = merged[-1][4] + "," + p[4] if p[4] not in merged[-1][4].split(",") else merged[-1][4]
            elif merged and p[0] < merged[-1][1]:
                # 重叠（相邻两条放宽后碰上了）：后一块从前一块的结尾开始
                cut = merged[-1][1] - p[0]
                p[0] += cut
                p[3] += cut
                if p[1] - p[0] > 0.05:
                    merged.append(p)
                elif p[4] not in merged[-1][4].split(","):
                    merged[-1][4] += "," + p[4]
            else:
                merged.append(p)
        seg["_pieces"] = merged
        # ── 片段
        first = merged[0][0]
        head = seg["head"]
        add_clip(i, seg, "head", first - head, head, aud=audio_src_at(take, first - head) if head > 0 else None)
        for k, p in enumerate(merged):
            m0, m1, src, t0, cid = p
            add_clip(i, seg, "speech", m0, m1 - m0, aud=(src, t0), cues=cid.split(","))
            for c_ in cid.split(","):
                cue_pieces.setdefault(c_, []).append(len(CLIPS) - 1)
            if k + 1 < len(merged):
                emit_gap(i, seg, m1, merged[k + 1][0], [])
        last = merged[-1][1]
        tail = seg["tail"]
        if isinstance(tail, list):            # ("to", 主时间)
            emit_gap(i, seg, last, tail[1], [])
        elif tail > 0:
            add_clip(i, seg, "tail", last, tail, aud=audio_src_at(take, last))
    # ── 成片时间
    t = 0
    for c in CLIPS:
        c["out0"] = t
        t += c["n"]
    total = t
    # ── 每条字幕在成片里的起止：按这条自己说话的主时间，换算到含有它的片段里
    def out_of(i, m, side):
        """段 i 的主时间 m → 成片帧号。m 落在剪掉的地方：起点取后一个片段的开头，终点取前一个片段的结尾。"""
        best = None
        for c in CLIPS:
            if c["seg"] != i or c["kind"] not in ("speech", "pause", "gap", "head", "tail"):
                continue
            c1 = c["m0"] + c["n"] / FPS * c["speed"]
            if c["m0"] - 1e-6 <= m <= c1 + 1e-6:
                return c["out0"] + (m - c["m0"]) / c["speed"] * FPS
            if side == "s" and c["m0"] > m and (best is None or c["m0"] < best[0]):
                best = (c["m0"], c["out0"])
            if side == "e" and c1 < m and (best is None or c1 > best[0]):
                best = (c1, c["out0"] + c["n"])
        return best[1] if best else None

    cues = []
    for i, seg in enumerate(segs):
        for q in seg["cues"]:
            if q.get("drop"):
                continue
            rg = cue_ranges.get(q["id"])
            if not rg:
                print("!! 字幕条没落到任何片段：", q["id"])
                continue
            s = out_of(i, min(r[0] for r in rg), "s")
            e = out_of(i, max(r[1] for r in rg), "e")
            cues.append({"id": q["id"], "zh": q["zh"], "seg": i, "out_s": round(s / FPS, 3), "out_e": round(e / FPS, 3)})
    for a, b in zip(cues, cues[1:]):
        if b["out_s"] < a["out_e"]:
            print(f"!! 字幕重叠 {a['id']}→{b['id']} {a['out_e']:.2f} > {b['out_s']:.2f}")
    # ── 叠在画面上的克隆配音（V2 这类：不占时间轴，放在某条字幕说完之后 gap 秒，比如 AI 生成的快进上）
    vox = []
    for v in data.get("vox", []):
        ref = next(q for q in cues if q["id"] == v["after"])
        s0 = ref["out_e"] + v.get("gap", 0.4)
        d = VO_DUR[v["src"]]
        vox.append({"id": v["id"], "src": v["src"], "out_s": round(s0, 3), "out_e": round(s0 + d, 3)})
        cues.append({"id": v["id"], "zh": v["zh"], "seg": ref["seg"], "out_s": round(s0 + 0.15, 3), "out_e": round(s0 + d - 0.2, 3), "vo": True})
    cues.sort(key=lambda q: q["out_s"])
    for a_, b_ in zip(cues, cues[1:]):
        if b_["out_s"] < a_["out_e"]:
            print(f"!! 配音和字幕重叠 {a_['id']}→{b_['id']}")
    # ── 拼人声
    levels = {}
    out = np.zeros((total * SR // FPS + SR, 2), np.float32)
    fade = int(0.012 * SR)
    for c in CLIPS:
        if not c["aud"]:
            continue
        src, t0 = c["aud"]
        if src not in levels:
            _, _, lev = env(src)
            levels[src] = TARGET_LEVEL - lev
        a = audio(src)
        n = c["n"] * SR // FPS
        s0 = int(round(t0 * SR))
        seg_a = np.zeros((n, 2), np.float32)
        if s0 < len(a):
            piece = a[max(0, s0): s0 + n]
            seg_a[max(0, -s0): max(0, -s0) + len(piece)] = piece
        seg_a *= 10 ** (levels[src] / 20)
        if n > 2 * fade:
            seg_a[:fade] *= np.linspace(0, 1, fade)[:, None]
            seg_a[-fade:] *= np.linspace(1, 0, fade)[:, None]
        o = c["out0"] * SR // FPS
        out[o: o + n] += seg_a
    for v in vox:
        src = v["src"]
        if src not in levels:
            levels[src] = TARGET_LEVEL - env(src)[2]
        a = audio(src) * 10 ** (levels[src] / 20)
        o = int(round(v["out_s"] * SR))
        n = min(len(a), len(out) - o)
        out[o: o + n] += a[:n]
    out = out[: total * SR // FPS]
    (HERE / "edit").mkdir(exist_ok=True)
    with wave.open(str(HERE / "edit" / "narration.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
    info = {"fps": FPS, "frames": total, "total": round(total / FPS, 3), "chapters": data["chapters"],
            "segs": [{k: v for k, v in s.items() if k not in ("cues", "_pieces")} for s in segs],
            "clips": CLIPS, "cues": cues, "vox": vox, "levels_db": {k: round(v, 1) for k, v in levels.items()}}
    (HERE / "edit" / "edit.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    # 汇总
    kinds = {}
    for c in CLIPS:
        kinds.setdefault(c["kind"], [0, 0])
        kinds[c["kind"]][0] += 1
        kinds[c["kind"]][1] += c["n"] / FPS
    print(f"成片 {total / FPS:.1f}s（{total} 帧），{len(CLIPS)} 个片段，{len(cues)} 条字幕")
    for k, (n, d) in kinds.items():
        print(f"  {k:7s} {n:4d} 个  {d:7.1f}s")
    for i, seg in enumerate(segs):
        cs = [c for c in CLIPS if c["seg"] == i]
        d = sum(c["n"] for c in cs) / FPS
        print(f"  段 {i:2d} {seg['take']} 版式{seg['layout']} 第{seg['chapter']}章：{d:6.1f}s  主时间 {cs[0]['m0']:.1f}–{cs[-1]['m0'] + cs[-1]['n'] / FPS * cs[-1]['speed']:.1f}")
    print("电平补偿（dB）：", info["levels_db"])


if __name__ == "__main__":
    main()
