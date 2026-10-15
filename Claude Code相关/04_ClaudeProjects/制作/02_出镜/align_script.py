# -*- coding: utf-8 -*-
r"""把悠一的口播（asr/*.json 的逐词时间）对回口播稿的每一句：每句稿子在识别结果里找最像的片段（重录的取最后一遍），出初稿 align_draft.json 和对照表 align_report.txt。

  python align_script.py

做法：汉字换成无声调拼音、英文词小写、数字逐位念成汉字，得到 token 序列；每句稿子和整个口播 token 流做“整句对齐、两端自由”的编辑距离对齐（numpy），
取得分的局部峰值作为这句的各遍录音（候选），再用动态规划挑一条“口播顺序单调向前”的路径：重录过的句子取最后一遍（得分差不多时偏后）。
识别有同音错字、英文专名常被写成中文音译，所以只看得分是否高，低分的人工核对。
"""
import json
import re
from pathlib import Path

import numpy as np
from pypinyin import Style, lazy_pinyin

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
CLIPS = ["0196", "0197", "0198", "0199", "0200"]
DIG = "零一二三四五六七八九"
SEP = "<sep>"


def toks_of(s):
    out = []
    for m in re.finditer(r"[一-鿿]|[A-Za-z]+|\d+(?:[.,]\d+)*", s):
        t = m.group(0)
        if "一" <= t[0] <= "鿿":
            out.append(lazy_pinyin(t, style=Style.NORMAL)[0])
        elif t[0].isdigit():
            out += [lazy_pinyin(DIG[int(d)], style=Style.NORMAL)[0] for d in re.sub(r"[.,]", "", t)]
        else:
            out.append(t.lower())
    return out


def build_stream():
    """所有录像的口播 token 流：[(token, clip, 开始秒, 结束秒)]；录像之间插一个分隔符。"""
    stream, text_at = [], []
    for c in CLIPS:
        d = json.loads((HERE / "asr" / f"{c}.json").read_text(encoding="utf-8"))
        for seg in d["segments"]:
            for w in seg["words"]:
                ts = toks_of(w["w"])
                for k, t in enumerate(ts):
                    a = w["s"] + (w["e"] - w["s"]) * k / max(1, len(ts))
                    b = w["s"] + (w["e"] - w["s"]) * (k + 1) / max(1, len(ts))
                    stream.append((t, c, a, b))
        stream.append((SEP, c, d["duration"], d["duration"]))
    return stream


def align_line(a, B, floor=-1e9):
    """a：这句稿子的 token；B：口播 token 流。返回每个终点 j 的最佳得分（整句 a 对齐到以 j 结尾的一段）。match +2，错配 −1，缺 / 多 −1。"""
    m, n = len(a), len(B)
    prev = np.zeros(n + 1, dtype=np.float32)                 # dp[0][j] = 0：起点自由
    Barr = np.array(B, dtype=object)
    for i in range(1, m + 1):
        sc = np.where(Barr == a[i - 1], 2.0, -1.0).astype(np.float32)
        sc[np.array([b == SEP for b in B])] = -3.0
        diag = prev[:-1] + sc
        x = np.empty(n + 1, dtype=np.float32)
        x[0] = prev[0] - 1.0
        x[1:] = np.maximum(diag, prev[1:] - 1.0)
        # y[j] = max(x[j], y[j-1] - 1)
        idx = np.arange(n + 1, dtype=np.float32)
        y = np.maximum.accumulate(x + idx) - idx
        prev = y
    return prev                                                # 长度 n+1，prev[j] = 以 b[:j] 结尾


def trace_start(a, B, j_end, win=None):
    """已知终点（B[:j_end]），回溯出起点。"""
    m = len(a)
    win = win or (m * 2 + 12)
    j0 = max(0, j_end - win)
    seg = B[j0:j_end]
    n = len(seg)
    dp = np.zeros((m + 1, n + 1), dtype=np.float32)
    for i in range(1, m + 1):
        dp[i, 0] = dp[i - 1, 0] - 1
        for j in range(1, n + 1):
            s = (2.0 if seg[j - 1] == a[i - 1] else -1.0) if seg[j - 1] != SEP else -3.0
            dp[i, j] = max(dp[i - 1, j - 1] + s, dp[i - 1, j] - 1, dp[i, j - 1] - 1)
    i, j = m, n
    while i > 0 and j > 0:
        s = (2.0 if seg[j - 1] == a[i - 1] else -1.0) if seg[j - 1] != SEP else -3.0
        if dp[i, j] == dp[i - 1, j - 1] + s:
            i, j = i - 1, j - 1
        elif dp[i, j] == dp[i - 1, j] - 1:
            i -= 1
        else:
            j -= 1
    return j0 + j


def main():
    lines = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))["lines"]
    stream = build_stream()
    B = [t[0] for t in stream]
    print(f"口播 token {len(B)} 个，稿子 {len(lines)} 句")
    cands = []
    for L in lines:
        a = toks_of(L["zh"])
        if not a:
            cands.append([])
            continue
        y = align_line(a, B)
        sc = y / (2.0 * len(a))
        # 局部峰值：得分 ≥ 0.40，且是前后 len(a) 范围内的最大值
        peaks = []
        order = np.argsort(-sc)
        taken = np.zeros(len(sc), dtype=bool)
        for j in order[:400]:
            if sc[j] < 0.40:
                break
            if taken[max(0, j - len(a)): j + len(a) + 1].any():
                continue
            taken[j] = True
            peaks.append(int(j))
            if len(peaks) >= 6:
                break
        cs = []
        for j in sorted(peaks):
            j0 = trace_start(a, B, j)
            if j0 >= j or j - 1 >= len(stream) or B[j - 1] == SEP:
                j = j - 1 if B[j - 1] == SEP else j
            seg = [t for t in stream[j0:j] if t[0] != SEP]
            if not seg:
                continue
            clip = seg[-1][1]
            seg = [t for t in seg if t[1] == clip]
            cs.append({"score": round(float(sc[j]) if j < len(sc) else 0, 3), "clip": clip, "s": round(seg[0][2], 2), "e": round(seg[-1][3], 2), "j0": j0, "j1": j})
        cands.append(cs)
    # 动态规划：每句选一个候选（或不选），口播位置单调向前；得分高优先，得分接近时偏后（取最后一遍）
    n = len(lines)
    best = [None] * n
    # state: (index of chosen candidate or -1) → (总分, 回指针)
    dp = []
    for i in range(n):
        row = {-1: (None, None)}
        for k, c in enumerate(cands[i]):
            row[k] = (None, None)
        dp.append(row)
    NEG = -1e9
    prev_best = {(-1, -1): 0.0}                                  # key = (上一个被选中的 j1) → 最优总分；-1 = 还没选过
    back = []
    cur = {-1: (0.0, None)}                                      # last_j1 → (分, 指针)
    for i in range(n):
        nxt = {}
        for last_j1, (tot, ptr) in cur.items():
            # 不选
            key = last_j1
            val = tot - 0.35                                      # 没对上的罚分
            if key not in nxt or val > nxt[key][0]:
                nxt[key] = (val, (last_j1, None))
            for k, c in enumerate(cands[i]):
                if c["j0"] < last_j1 - 2:                         # 必须在上一句之后（允许 2 个 token 的重叠误差）
                    continue
                bonus = 0.0005 * c["j1"] / 10.0                    # 得分相近时偏后
                val = tot + c["score"] + bonus
                key = c["j1"]
                if key not in nxt or val > nxt[key][0]:
                    nxt[key] = (val, (last_j1, k))
        back.append(nxt)
        cur = nxt
    # 回溯
    key = max(cur, key=lambda k: cur[k][0])
    choice = [None] * n
    for i in range(n - 1, -1, -1):
        val, (last, k) = back[i][key]
        choice[i] = k
        key = last
    # 输出
    out, rep = [], []
    for i, L in enumerate(lines):
        c = cands[i][choice[i]] if choice[i] is not None else None
        out.append({"id": L["id"], "zh": L["zh"], "chosen": c, "cands": cands[i]})
        if c:
            seg = [t for t in stream[c["j0"]:c["j1"]] if t[0] != SEP]
            txt = ""
            # 取这段识别原文
            rep.append(f"{L['id']}  {c['clip']} {c['s']:7.2f}–{c['e']:7.2f}  得分 {c['score']:.2f}  共 {len(cands[i])} 遍  | {L['zh']}")
        else:
            rep.append(f"{L['id']}  —— 没对上（候选 {len(cands[i])}） | {L['zh']}")
    (HERE / "align_draft.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "align_report.txt").write_text("\n".join(rep) + "\n", encoding="utf-8")
    ok = sum(1 for o in out if o["chosen"])
    lowq = sum(1 for o in out if o["chosen"] and o["chosen"]["score"] < 0.6)
    print(f"对上 {ok}/{n} 句，其中得分 < 0.6 的 {lowq} 句；没对上 {n - ok} 句。详见 align_report.txt")


if __name__ == "__main__":
    main()
