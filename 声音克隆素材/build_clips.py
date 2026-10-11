# -*- coding: utf-8 -*-
"""把真人出镜口播（干净人声，不含 BGM）切成 Fish Audio「专业声音克隆」要的片段。

规格来源：Fish Audio 官方博客《专业声音克隆》（2026-06-15）
  MP3 / WAV / FLAC；总共 10–180 分钟；每段控制在 1 分钟以内，最佳是 12–15 段、每段 45–60 秒、语调一致；
  有背景噪音、长段空白、音效的片段会被判不合格。
  （登录后草稿页上的现行要求以页面为准，改了规格就改下面的常量重跑。）

做法
  1. 口播来源：各期 制作/02_出镜/edit/narration.wav（48 kHz 立体声，已去口癖、去重录、长停顿缩短，不含 BGM 和音效）。
  2. 切点：整条口播里所有自然停顿——安静（< QUIET_DB）不短于 MIN_RUN，停顿之前话音是自然收尾（紧邻两帧 ≤ PRE_DB）、
     停顿之后不是硬切起音（紧邻一帧 ≤ POST_DB）。剪辑时逐句拼接的接缝里有一部分话音没落完（收尾处 −17～−25 dB），不当切点。
  3. 动态规划分组：每段 ≤ MAXLEN，尽量落在 GOOD_LO–MAXLEN，优先在长停顿处断开，段中间不留 ≥ 1 s 的长停顿。
  4. 输出 48 kHz 单声道 16-bit WAV；切点两端各 10 ms 淡入淡出（首尾若还带着声音，加长到 50 ms）；不降噪、不压缩、不改响度。
  5. 文字稿：取和这一段重叠的字幕条（字幕文本，不是逐字稿；括号注释已去掉）。

用法
  python build_clips.py --plan     只打印分组方案，不写文件（-v 同时打印切点表）
  python build_clips.py            渲染到 上传用/，写 分段清单.json
"""
import bisect
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
OUT = HERE / "上传用"

# 口播来源：(前缀, 说明, 出镜目录)
SOURCES = [
    ("ep1", "AI时代计算机研究生 第1期《别再用VSCode了》",
     Path(r"D:\大疆\.claude\worktrees\ai-era-cs-grad-skills-1a823b\AI震惊瘫坐时代计算机研究生必须掌握的技能\01_别再用VSCode了\制作\02_出镜")),
    ("wta02", "Way to AGI 第2期《如何使用Claude来低成本的生成视频》",
     Path(r"D:\大疆\Way to AGI\02_如何使用Claude来低成本的生成视频\制作\02_出镜")),
]

MAXLEN = 58.0          # 每段上限（官方是 1 分钟以内，留 2 s 余量）
GOOD_LO = 48.0         # 每段理想下限（官方建议 45–60 s）
LEAD, TAIL = 0.20, 0.30    # 段首、段尾各留多少静音
FADE, FADE_LONG = 0.010, 0.050
HOP = 0.010            # 能量帧
QUIET_DB = -46.0       # 安静：说话电平约 −14.5 dB，底噪约 −66 dB
PRE_DB = -30.0         # 安静段之前紧邻两帧（20 ms）的能量：话音自然收尾，不是被剪辑切断（切断的是 −17～−25 dB）
POST_DB = -24.0        # 安静段之后紧邻第一帧：起音不是硬切（起音本来就陡，比收尾放松）
MIN_RUN = 0.15         # 切点所在的安静段至少这么长
LONG_PAUSE = 1.0       # 段中间不想留的长停顿
INNER_PAUSE_KEEP = 0.6 # 万一还是留了，压到这么长（静音里拼接，不会有咔嗒声）
MAX_INNER_PAUSE = 1.2


def strip_notes(t):
    """字幕里的括号注释是没说出口的话，清单里去掉。"""
    return re.sub(r"[（(][^）)]*[）)]", "", t).strip()


def load_source(root):
    edit = json.loads((root / "edit" / "edit.json").read_text(encoding="utf-8"))
    x, sr = sf.read(root / "edit" / "narration.wav", dtype="float32", always_2d=True)
    m = x.mean(axis=1)          # (L+R)/2：L/R 相关系数 0.8，实测没有梳状滤波
    return edit, m, sr


def energy_db(m, sr):
    hop = int(sr * HOP)
    n = len(m) // hop
    fr = m[: n * hop].reshape(n, hop)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-9)


def quiet_runs(db):
    """所有连续安静帧 [(起帧, 止帧)]。"""
    q, out, i = db < QUIET_DB, [], 0
    while i < len(q):
        if q[i]:
            j = i
            while j < len(q) and q[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def plan_source(edit, m, sr, verbose=False):
    total = len(m) / sr
    db = energy_db(m, sr)
    runs = quiet_runs(db)
    active = np.where(db > QUIET_DB)[0]
    first_sound, last_sound = active[0] * HOP, (active[-1] + 1) * HOP

    # 候选切点：自然停顿
    cand = []
    for k0, k1 in runs:
        L = (k1 - k0) * HOP
        if L < MIN_RUN or k0 < 2 or k1 >= len(db) - 1:
            continue
        pre, post = float(db[k0 - 2:k0].max()), float(db[k1])
        if pre <= PRE_DB and post <= POST_DB:
            cand.append({"rs": k0 * HOP, "re": k1 * HOP, "gap": L, "pre": pre, "post": post})
    if verbose:
        print("  候选切点 %d 个：" % len(cand))
        for i, c in enumerate(cand):
            print("    %3d  %8.2f-%8.2f  长 %.2f  前 %6.1f  后 %6.1f" % (i, c["rs"], c["re"], c["gap"], c["pre"], c["post"]))

    # 段落的起点/终点：-1 = 文件开头，len(cand) = 文件结尾
    def start_of(a):
        if a < 0:
            return max(0.0, first_sound - LEAD)
        c = cand[a]
        return max((c["rs"] + c["re"]) / 2, c["re"] - LEAD)

    def end_of(b):
        if b >= len(cand):
            return min(total, last_sound + TAIL)
        c = cand[b]
        return min((c["rs"] + c["re"]) / 2, c["rs"] + TAIL)

    # 段中间不想留的长停顿（整段落在里面的安静段）
    longs = sorted((k0 * HOP, k1 * HOP) for k0, k1 in runs if (k1 - k0) * HOP >= LONG_PAUSE)
    long_starts = [a for a, _ in longs]

    def inner_longs(s, e):
        n = 0
        for idx in range(bisect.bisect_left(long_starts, s + 0.05), len(longs)):
            if longs[idx][0] > e:
                break
            if longs[idx][1] <= e - 0.05:
                n += 1
        return n

    def cut_cost(b):
        if b >= len(cand):
            return 0.0
        g = cand[b]["gap"]
        return 0.0 if g >= 0.6 else 0.5 if g >= 0.4 else 1.5 if g >= 0.25 else 3.0

    N = len(cand)
    INF = 1e18
    best = {-1: 0.0}
    prev = {}
    for b in range(0, N + 1):               # 这一段以切点 b 结束（N = 文件结尾）
        eb = end_of(b)
        best[b] = INF
        for a in range(-1, b):              # 从切点 a 开始（-1 = 文件开头）
            if best[a] >= INF:
                continue
            s = start_of(a)
            L = eb - s
            if L <= 0 or L > MAXLEN:
                continue
            c = 1.0 + (0.0 if L >= GOOD_LO else (GOOD_LO - L) ** 2 / 20.0)
            c += 6.0 * inner_longs(s, eb) + cut_cost(b)
            if best[a] + c < best[b]:
                best[b], prev[b] = best[a] + c, a
    assert best[N] < INF, "分不出来：候选切点太少，放宽 EDGE_DB / MIN_RUN"
    cuts, b = [], N
    while b != -1:
        a = prev[b]
        cuts.append((a, b))
        b = a
    cuts.reverse()

    cues = edit["cues"]
    plan = []
    for a, b in cuts:
        s, e = start_of(a), end_of(b)
        texts = []
        for c in cues:
            dur = max(1e-6, c["out_e"] - c["out_s"])
            inside = max(0.0, min(e, c["out_e"]) - max(s, c["out_s"])) / dur
            if inside >= 0.5:
                t = strip_notes(c["zh"])
                texts.append(t if inside >= 0.85 else "…" + t + "…")     # ASR 句首时间比真实起声早 ~0.3 s，别卡太严
        plan.append({"s": s, "e": e, "text": "".join(texts), "inner_long": inner_longs(s, e),
                     "cut_gap": cand[b]["gap"] if b < N else None})
    return plan, cand


def compress_inner_pauses(seg, sr):
    """段中间 > MAX_INNER_PAUSE 的停顿压到 INNER_PAUSE_KEEP（在静音里拼接）。返回新数组和压掉了几处。"""
    db = energy_db(seg, sr)
    quiet = db < QUIET_DB
    hop = int(sr * HOP)
    out, cur, n_cut, i, n = [], 0, 0, 0, len(quiet)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            L = (j - i) * HOP
            if L > MAX_INNER_PAUSE and i > 0 and j < n:        # 只动段中间的
                keep = int(INNER_PAUSE_KEEP * sr / 2)
                out.append(seg[cur: i * hop + keep])
                cur = j * hop - keep
                n_cut += 1
            i = j
        else:
            i += 1
    out.append(seg[cur:])
    return np.concatenate(out), n_cut


def fade(seg, sr):
    """首尾淡入淡出；如果首尾 20 ms 还带着声音（文件头尾的话音被剪辑切断的），加长到 FADE_LONG。"""
    seg = seg.copy()
    e20 = int(0.02 * sr)
    edge_in = 20 * np.log10(np.sqrt((seg[:e20] ** 2).mean()) + 1e-9)
    edge_out = 20 * np.log10(np.sqrt((seg[-e20:] ** 2).mean()) + 1e-9)
    k_in = int((FADE_LONG if edge_in > -50 else FADE) * sr)
    k_out = int((FADE_LONG if edge_out > -50 else FADE) * sr)
    seg[:k_in] *= np.linspace(0, 1, k_in, dtype=np.float32)
    seg[-k_out:] *= np.linspace(1, 0, k_out, dtype=np.float32)
    return seg


def main():
    plan_only = "--plan" in sys.argv
    verbose = "-v" in sys.argv
    manifest = []
    for prefix, label, root in SOURCES:
        edit, m, sr = load_source(root)
        plan, cand = plan_source(edit, m, sr, verbose)
        print("=" * 72)
        print(prefix, label, "| %.1f s | 自然停顿候选 %d 个" % (len(m) / sr, len(cand)))
        for k, p in enumerate(plan, 1):
            name = "%s_%02d.wav" % (prefix, k)
            p["file"], p["source"], p["source_label"] = name, prefix, label
            print("  %s  %7.2f - %7.2f  (%.2f s)  段尾停顿 %s  段中长停顿 %d" % (
                name, p["s"], p["e"], p["e"] - p["s"], "%.2f s" % p["cut_gap"] if p["cut_gap"] else "文件结尾", p["inner_long"]))
            if not plan_only:
                OUT.mkdir(exist_ok=True)
                seg = m[int(p["s"] * sr): int(p["e"] * sr)]
                seg, n_cut = compress_inner_pauses(seg, sr)
                p["inner_pauses_compressed"] = n_cut
                p["dur"] = len(seg) / sr
                sf.write(OUT / name, fade(seg, sr), sr, subtype="PCM_16")
            manifest.append(p)
        print("  合计 %d 段，%.1f s" % (len(plan), sum(p["e"] - p["s"] for p in plan)))
    if not plan_only:
        (HERE / "分段清单.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        print("写出", len(manifest), "段 →", OUT)


if __name__ == "__main__":
    main()
