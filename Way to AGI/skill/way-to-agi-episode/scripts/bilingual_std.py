# -*- coding: utf-8 -*-
"""项目统一的中英双语字幕标准（用户 2026-10-02：“看一下其他分集的 skill 中的字幕要求……统一用那个双语标准”）的代码实现。

标准来源：本技能 `references/subtitles.md`「中英双语」+ `references/pipeline.md` §2，样式取自模板 `assets/template/制作/03_成片/index.html` 的 `#subs` / `#subZh` / `#subEn`。
  - 居中，字幕带在 y 922 以下（带高 130）：中文一行 52 px / 行高 66（Noto Sans SC 800，墨黑 #1B1B1F，白边 10 px 描边）、英文一行 30 px / 行高 40
    （600，灰 #4B5563，白边 6 px），英文从带顶往下 70 px；各一行、不换行。
  - 一条字幕 1–2 句，中文 ≤ 约 28 字、英文 ≤ 约 90 字符（括号注释算在内）；放不下就拆成多条（本模块的 split_pair 自动拆，句内按标点 / 连词找边界）。
  - 每条开始前 0.1 s 显示到结束后 0.45 s，不和下一条重叠。
  - 导出三份 SRT：双语（中文在上）/ 中文 / 英文。

提供：
  zh_units(s)                    中文行的宽度，按“字”算（汉字 / 全角标点 = 1，英文字母数字 ≈ 0.55，空格 ≈ 0.3 …）
  split_pair_aligned(zh, en, prefix_units=0, cuts=None)   **新片子用这个**：把一对（中文, 英文）拆成 n 条，中英文一起找断点（断在标点 / 语义处、两边对得上），
                                 cuts = [(中文锚点, 英文锚点), …] 可以手动指定断点 → [(zh_i, en_i, 中文占的宽度)]
  split_pair(zh, en, prefix_units=0)   旧版：先拆中文、再让英文凑同样的占比，会断在“政策 | 的航班”这类地方（已经渲好的片子用的是它，留着复现）
  chunk_times(s, e, chunks)      把整句的起止时间按中文宽度占比分给每一条 → [(s_i, e_i)]
  display_windows(items)         [(s, e)] → 每条的显示区间（前 LEAD、后 LAG，互不重叠）
  ass_header(...) / ass_events(...) / write_srts(...)   烧进画面用的 ASS 和三份 SRT
独立视频里的现成用法：`独立视频/2026-10_ClaudeSlides设计师用法/制作/00_整片/make_subs.py`（外来视频烧字幕）、
`独立视频/2026-10_OpenAI视频中文版/制作/00_整片/make_ass.py`、`独立视频/2026-10_OpenAI-DevDay-2026解读/制作/00_整片/build_timeline.py`（引擎里画字幕）。
"""
import re

ZH_PX, EN_PX = 52, 30
BAND_TOP = 922
ZH_CY = BAND_TOP + 33                 # 中文行的垂直中心：带顶 + 行高 66 的一半
EN_CY = BAND_TOP + 70 + 20            # 英文行的垂直中心：带顶 + 70 + 行高 40 的一半
LEAD, LAG = 0.1, 0.45
ZH_MAX, EN_MAX = 28.5, 90
INK, GREY, ORANGE = "&H001F1B1B", "&H00635B4B", "&H001A4FFF"        # #1B1B1F、#4B5563、#FF4F1A（ASS 是 BGR）

_PUNCT_ZH = "，。！？；：、"
_CLOSE = "”’）)》」』】"


def zh_units(s):
    """中文行宽度（单位：一个汉字宽）。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if ch == " ":
            w += 0.3
        elif o < 128:
            w += 0.58 if ch.isupper() or ch.isdigit() else 0.52 if ch.isalpha() else 0.38
        else:
            w += 1.0
    return w


def en_len(s):
    return len(s)


# ---------------------------------------------------------------- 拆中文
_PREP = set("在把对给从用让被向跟同为比于")
_CONJ_START = ("而且", "但是", "但", "所以", "因为", "如果", "然后", "并且", "还有", "不过", "只是", "可是", "同时", "再", "就", "也", "还", "才", "先", "又", "既然", "虽然", "要是", "比如", "包括", "以及", "或者")
_UNIT_START = tuple("点分钟小时秒天年月日号美元元倍个万亿%")


def _zh_candidates(zh):
    """可以断开的位置（断在该下标之前）及代价：标点后 0；用 jieba 分词，只在词与词之间断；连词 / 副词前代价小，
    介词和它的宾语之间、数字和单位之间代价很大。不拆英文单词 / 数字串。返回 [(pos, penalty)]。"""
    try:
        import jieba
        toks = [t for t in jieba.cut(zh) if t]
    except Exception:
        toks = list(zh)
    cands, pos = [], 0
    for k, t in enumerate(toks[:-1]):
        pos += len(t)
        nxt = toks[k + 1]
        last = t[-1]
        if last in _PUNCT_ZH or (last in _CLOSE and len(t) >= 2 and t[-2] in _PUNCT_ZH):
            if nxt[0] not in _PUNCT_ZH and nxt[0] not in _CLOSE:
                cands.append((pos, 0.0))
            continue
        if nxt[0] in _PUNCT_ZH or nxt[0] in _CLOSE:
            continue
        pen = 40.0
        if nxt.startswith(_CONJ_START):
            pen = 12.0
        if t.strip() == "":
            pen = 25.0
        if t in _PREP or (len(t) == 1 and last in _PREP):
            pen = 160.0
        if (t[-1].isdigit() or t[-1] in ":%") and nxt.startswith(_UNIT_START):
            pen = 160.0
        if t[-1] in "“‘（([《「『【":
            continue
        cands.append((pos, pen))
    return cands


def _split_zh(zh, n, prefix_units=0.0):
    """把中文拆成 n 段：动态规划，目标是各段宽度接近，少在没有标点的地方断；返回 [段] 或 None（凑不出每段 ≤ ZH_MAX）。"""
    if n == 1:
        return [zh] if zh_units(zh) + prefix_units <= ZH_MAX else None
    cands = _zh_candidates(zh)
    pos = [0] + [p for p, _ in cands] + [len(zh)]
    pen = {p: c for p, c in cands}
    total = zh_units(zh) + prefix_units
    target = total / n
    INF = 1e18
    # best[k][j]：用 k 段把 zh[:pos[j]] 切完的最小代价
    best = [[INF] * len(pos) for _ in range(n + 1)]
    back = [[-1] * len(pos) for _ in range(n + 1)]
    best[0][0] = 0.0
    for k in range(1, n + 1):
        for j in range(1, len(pos)):
            for i in range(j):
                if best[k - 1][i] >= INF:
                    continue
                seg = zh[pos[i]:pos[j]]
                u = zh_units(seg) + (prefix_units if i == 0 else 0.0)
                if u > ZH_MAX:
                    continue
                cost = best[k - 1][i] + (u - target) ** 2 + (pen.get(pos[i], 0.0) if i > 0 else 0.0)
                if cost < best[k][j]:
                    best[k][j], back[k][j] = cost, i
    j = len(pos) - 1
    if best[n][j] >= INF:
        return None
    out, k = [], n
    while k > 0:
        i = back[k][j]
        out.append(zh[pos[i]:pos[j]])
        j, k = i, k - 1
    return out[::-1]


# ---------------------------------------------------------------- 拆英文
_BREAK_BEFORE = {"and", "but", "so", "because", "which", "that", "who", "where", "when", "while", "then", "or", "to", "with", "for", "if", "as", "than", "like"}


def _en_candidates(words):
    """可以断开的位置（断在第 i 个词之前，1 ≤ i < len）：逗号 / 句号后最优，连词前次之，其余较差。返回 {i: penalty}。"""
    pen = {}
    for i in range(1, len(words)):
        prev, cur = words[i - 1], words[i].lower().strip(",.;:!?\"'()")
        if prev.endswith((".", "?", "!", "…")):
            pen[i] = 0.0
        elif prev.endswith((",", ";", ":", "—", "–")):
            pen[i] = 0.02
        elif cur in _BREAK_BEFORE:
            pen[i] = 0.12
        else:
            pen[i] = 0.35
    return pen


def _split_en(en, fracs):
    """把英文按给定的累计占比（长度 n−1 的列表）拆成 n 段：每个断点选最接近占比的、标点 / 连词优先的位置；返回 [段] 或 None（凑不出每段 ≤ EN_MAX）。"""
    words = en.split()
    n = len(fracs) + 1
    if n == 1:
        return [en] if len(en) <= EN_MAX else None
    if len(words) < n:
        return None
    pen = _en_candidates(words)
    cum, acc = [0], 0
    for w in words:
        acc += len(w) + 1
        cum.append(acc)
    total = cum[-1]
    INF = 1e18
    idx = sorted(pen)
    # best[k][j]：已经放了 k 个断点、最后一个断点在 idx[j] 的最小代价
    best = [[INF] * len(idx) for _ in range(n)]
    back = [[-1] * len(idx) for _ in range(n)]
    for j, p in enumerate(idx):
        best[1][j] = abs(cum[p] / total - fracs[0]) + pen[p]
    for k in range(2, n):
        for j, p in enumerate(idx):
            for i, q in enumerate(idx):
                if q < p and best[k - 1][i] < INF:
                    c = best[k - 1][i] + abs(cum[p] / total - fracs[k - 1]) + pen[p]
                    if c < best[k][j]:
                        best[k][j], back[k][j] = c, i
    j = min(range(len(idx)), key=lambda t: best[n - 1][t])
    if best[n - 1][j] >= INF:
        return None
    cuts, k = [], n - 1
    while k >= 1:
        cuts.append(idx[j])
        j, k = back[k][j], k - 1
    cuts = cuts[::-1]
    segs, a = [], 0
    for c in cuts + [len(words)]:
        segs.append(" ".join(words[a:c]))
        a = c
    return segs if all(len(s) <= EN_MAX for s in segs) else None


def split_pair(zh, en, prefix_units=0.0, max_n=8):
    """(中文, 英文) → [(中文段, 英文段, 中文占的宽度)]。从最少需要的条数开始试：中文 ≤ ZH_MAX 字、英文 ≤ EN_MAX 字符，凑不出就多拆一条。
    prefix_units = 第一条中文前面还要放的东西（比如“dot：”标签）占的字宽。"""
    zh, en = zh.strip(), re.sub(r"\s+", " ", en.strip())
    n0 = max(1, int(-(-(zh_units(zh) + prefix_units) // ZH_MAX)), int(-(-len(en) // EN_MAX)))
    for n in range(n0, max_n + 1):
        zs = _split_zh(zh, n, prefix_units)
        if not zs:
            continue
        tot = sum(zh_units(z) for z in zs)
        cum, fr = 0.0, []
        for z in zs[:-1]:
            cum += zh_units(z)
            fr.append(cum / tot)
        es = _split_en(en, fr) if n > 1 else ([en] if len(en) <= EN_MAX else None)
        if es:
            return [(z, e, zh_units(z)) for z, e in zip(zs, es)]
    return [(zh, en, zh_units(zh))]         # 实在拆不开：整条放，由调用方报出来


# ---------------------------------------------------------------- 对齐版拆条：中英文一起找断点
# split_pair 先拆中文、再让英文去凑同样的占比，中文会断在“自己的 | Dot”“挺 | 大胆”这类地方，中英两条的内容也常对不上。
# 对齐版把（中文断点, 英文断点）当成一对一起选：优先断在标点后、两边断在同样的语义位置（占比接近），
# 不在“的 / 了 / 吗”前、英文词组（Agent 365）和数字串里、孤零零的“我 / 你 / 它”后面、英文冠词 / 介词 / 连词后面断。
# 旧的 split_pair 不动（独立视频里已渲好的片子用的是它）；新做的片子用这个，拆得还不顺的地方再用 cuts 手动指定。
EN_SOFT = 94                         # 对齐版里英文可以比 EN_MAX 多几个字符（“约 90”），超出的部分要扣分
_CONJ_START_STRONG = ("而且", "但是", "但", "所以", "因为", "如果", "然后", "并且", "还有", "不过", "只是", "可是", "同时", "既然", "虽然", "要是", "比如", "包括", "以及", "或者")
_ZH_PARTICLES = {"的", "地", "得", "了", "着", "过", "吗", "呢", "吧", "啊", "呀", "嘛", "们"}
_ZH_PRON = {"我", "你", "他", "她", "它", "咱", "我们", "你们", "他们", "她们", "咱们", "大家"}
_ZH_FUNC = {"的", "地", "得", "很", "最", "更", "太", "不", "没", "没有", "都", "也", "就", "才", "还", "先", "又", "再", "已经", "正在", "会", "能", "要", "可以",
            "应该", "将", "把", "被", "让", "给", "对", "向", "从", "在", "用", "为", "和", "与", "跟", "同", "及", "或", "但", "而", "并", "这", "那", "每", "各", "某"}
_EN_NO_BREAK_AFTER = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "with", "by", "from", "into", "my", "your", "our", "their", "its", "his",
                      "her", "this", "these", "those", "some", "any", "no", "and", "or", "but", "so", "that", "is", "are", "was", "were", "be", "than",
                      "as", "if", "not", "just", "also", "really", "very", "about", "over", "up", "out", "off", "i", "you", "we", "they", "it", "he", "she"}
_EN_NO_BREAK_AFTER |= {"plus", "while", "when", "because", "which", "who", "where", "then", "also", "even", "only", "both", "each", "every", "other",
                       "another", "many", "much", "more", "most", "such", "own", "same", "like", "per", "via", "all", "very",
                       "already", "still", "now", "always", "never", "often", "actually", "basically", "simply", "directly", "soon", "finally", "currently"}
_EN_PAIRS = {("start", "to"), ("up", "to"), ("due", "to"), ("close", "to"), ("next", "to"), ("according", "to"), ("such", "as"), ("as", "well"),
             ("in", "order"), ("kind", "of"), ("lot", "of"), ("a", "lot"), ("out", "of"), ("one", "of"), ("able", "to"), ("how", "to"), ("want", "to"),
             ("need", "to"), ("going", "to"), ("have", "to")}
_EN_AUX = {"can", "will", "would", "could", "should", "may", "might", "must", "has", "have", "had", "is", "are", "was", "were", "does", "did", "it's", "that's"}   # 主语 | 谓语：自然的断点
_EN_COMPARATIVE = {"more", "less", "rather", "better", "worse", "greater", "fewer", "higher", "lower", "bigger", "faster", "larger"}


def _ascii_word_char(ch):
    return ch.isascii() and (ch.isalnum() or ch in "&%$")


def _zh_candidates2(zh):
    """_zh_candidates 的加强版（对齐版用）：返回 [(pos, penalty)]，pos = 下一条从这里开始（已跳过中间的空格）。"""
    try:
        import jieba
        toks = [t for t in jieba.cut(zh) if t]
    except Exception:
        toks = list(zh)
    real, pos = [], 0
    for t in toks:
        if t.strip():
            real.append((pos + (len(t) - len(t.lstrip())), t.strip()))
        pos += len(t)
    cands = []
    for k in range(len(real) - 1):
        t, (cut, nxt) = real[k][1], real[k + 1]
        last = t[-1]
        endp = last if last in _PUNCT_ZH else (t[-2] if (last in _CLOSE and len(t) >= 2 and t[-2] in _PUNCT_ZH) else "")
        if endp:
            if nxt[0] not in _PUNCT_ZH and nxt[0] not in _CLOSE:
                cands.append((cut, -10.0 if endp in "。！？" else 20.0 if endp == "、" else 0.0))   # 句末最好，顿号（列举中间）不如逗号
            continue
        if nxt[0] in _PUNCT_ZH or nxt[0] in _CLOSE or last in "“‘（([《「『【@#":
            continue
        if _ascii_word_char(last) and _ascii_word_char(nxt[0]):          # 英文词组 / 数字串中间：Agent 365、Silver Lake Pool & Inn
            continue
        if nxt in _ZH_PARTICLES or nxt[0] in "的地得":                    # 的 / 了 / 吗 不能放在一条的开头
            continue
        pen = 40.0
        if nxt.startswith(_CONJ_START_STRONG):                             # 连词前：可以断；就 / 也 / 还 这类副词前不算
            pen = 12.0
        if t in _PREP or (len(t) == 1 and last in _PREP):
            pen = 160.0
        if (last.isdigit() or last in ":%") and nxt.startswith(_UNIT_START):
            pen = 160.0
        if t in _ZH_PRON or t in _ZH_FUNC:                                 # “我 | 是不是”“你的 | 产品”“很 | 重要”：虚词 / 代词不放在一条的末尾
            pen = max(pen, 160.0)
        cands.append((cut, pen))
    return cands


def _en_candidates2(words):
    """_en_candidates 的加强版：冠词 / 介词 / 连词 / 代词后面、“more | than”、数字后面不断。返回 {i: penalty}（断在第 i 个词之前）。"""
    out = {}
    for i in range(1, len(words)):
        prev = words[i - 1].rstrip("\"'”’)")
        pl = prev.lower().strip(",.;:!?\"'()“”")
        cur = words[i].lower().strip(",.;:!?\"'()“”")
        if prev.endswith((".", "?", "!", "…")):
            p = -0.05
        elif prev.endswith((",", ";", ":", "—", "–")):
            p = 0.03
        else:
            p = 0.18 if cur in _BREAK_BEFORE else 0.30 if cur in _EN_AUX else 0.52
            if pl in _EN_NO_BREAK_AFTER:
                p += 1.0
            if (pl, cur) in _EN_PAIRS:
                p += 1.0
            if cur == "than" and pl in _EN_COMPARATIVE:
                p += 1.0
            if any(c.isdigit() for c in prev):
                p += 0.3
        out[i] = p
    return out


def _manual_chunks(zh, en, cuts):
    """cuts = [(中文锚点, 英文锚点), …]：每一对表示“中文在这段文字之后断、英文在这段文字之后断”（按出现的先后找）。"""
    zp = ep = 0
    zs, es = [0], [0]
    for za, ea in cuts:
        zi = zh.index(za, zp) + len(za)
        ei = en.index(ea, ep) + len(ea)
        zs.append(zi)
        es.append(ei)
        zp, ep = zi, ei
    zs.append(len(zh))
    es.append(len(en))
    return [(zh[a:b].strip(), en[c:d].strip(), zh_units(zh[a:b].strip())) for a, b, c, d in zip(zs, zs[1:], es, es[1:])]


def split_pair_aligned(zh, en, prefix_units=0.0, max_n=6, cuts=None):
    """(中文, 英文) → [(中文段, 英文段, 中文占的宽度)]，和 split_pair 同样的约束（中文 ≤ ZH_MAX 字，英文 ≤ EN_MAX 字符，
    对齐版允许英文到 EN_SOFT 但要扣分），但是中英断点一起选。
    cuts = [(中文锚点, 英文锚点), …]：手动指定断点（自动拆得不顺的句子用），给了就不再自动拆。
    选法：从最少需要的条数 n0 试到 n0+1，总代价最小的那个。代价 = Σ 断点处的代价（中文标点后 0、连词前小、其余大；英文标点后 ≈ 0、连词前小、其余大）
    + 2 × |中文断点占比 − 英文断点占比|（让两边断在同一个语义位置）+ 太短的条（中文 < 7 字、英文 < 18 字符）的扣分 + 每多一条的固定代价。"""
    zh, en = zh.strip(), re.sub(r"\s+", " ", en.strip())
    if cuts:
        return _manual_chunks(zh, en, cuts)
    words = en.split()
    ztot = zh_units(zh) or 1.0
    n0 = max(1, int(-(-(ztot + prefix_units) // ZH_MAX)), int(-(-len(en) // EN_MAX)))
    if n0 == 1:                                              # 一条放得下：不用拆
        return [(zh, en, zh_units(zh))]
    if not words or n0 > max_n:
        return split_pair(zh, en, prefix_units, max_n)
    zc = _zh_candidates2(zh)
    zpen = dict(zc)
    zpos = sorted(zpen)
    ec = _en_candidates2(words)
    epos = sorted(ec)
    cumz = [0.0]
    for ch in zh:
        cumz.append(cumz[-1] + zh_units(ch))
    cume = [0]
    for w in words:
        cume.append(cume[-1] + len(w) + 1)
    etot = cume[-1]
    states = []                                              # 内部断点 (a, b, 代价)
    for a in zpos:
        fa = cumz[a] / ztot
        for b in epos:
            fb = cume[b] / etot
            if abs(fa - fb) <= 0.3:
                states.append((a, b, zpen[a] / 60.0 + ec[b] + 2.0 * abs(fa - fb) + 0.25))
    states.sort()
    nz, nw = len(zh), len(words)

    def solve(n):
        INF = 1e18
        target = (ztot + prefix_units) / n

        def size_cost(uz, le):
            c = 0.5 * ((uz - target) / target) ** 2                  # 各条中文宽度接近
            if uz < 10:
                c += (10 - uz) ** 2 * 0.04                           # 太短（显示不到 1.5 s）
            if le < 26:
                c += (26 - le) ** 2 * 0.0015
            if le > EN_MAX:
                c += (le - EN_MAX) * 0.25                            # 英文超过 90 字符：能不超就不超
            return c

        layer = {(0, 0): (0.0, None)}                        # 已经放了 k 个断点，最后一个断点在 (a, b)
        layers = [layer]
        for k in range(1, n):
            nxt = {}
            for (pa, pb), (pc, _) in layer.items():
                for a, b, bc in states:
                    if a <= pa or b <= pb:
                        continue
                    uz = cumz[a] - cumz[pa] + (prefix_units if pa == 0 else 0.0)
                    le = cume[b] - cume[pb] - 1
                    if uz > ZH_MAX or le > EN_SOFT:
                        continue
                    c = pc + bc + size_cost(uz, le)
                    if c < nxt.get((a, b), (INF,))[0]:
                        nxt[(a, b)] = (c, (pa, pb))
            layer = nxt
            layers.append(layer)
        best, arg = INF, None
        for (pa, pb), (pc, _) in layer.items():
            uz = cumz[nz] - cumz[pa] + (prefix_units if pa == 0 else 0.0)
            le = cume[nw] - cume[pb] - 1
            if uz > ZH_MAX or le > EN_SOFT or pa >= nz or pb >= nw:
                continue
            c = pc + size_cost(uz, le)
            if c < best:
                best, arg = c, (pa, pb)
        if arg is None:
            return INF, None
        path, cur = [], arg
        for k in range(n - 1, 0, -1):
            path.append(cur)
            cur = layers[k][cur][1]
        return best, path[::-1]

    results = [solve(n) for n in range(n0, min(max_n, n0 + 1) + 1)]
    results = [r for r in results if r[1] is not None]
    if not results:
        return split_pair(zh, en, prefix_units, max_n)
    _, path = min(results, key=lambda r: r[0])
    zs = [0] + [a for a, _ in path] + [nz]
    es = [0] + [b for _, b in path] + [nw]
    out = []
    for a, b, c, d in zip(zs, zs[1:], es, es[1:]):
        z = zh[a:b].strip()
        out.append((z, " ".join(words[c:d]), zh_units(z)))
    return out


def chunk_times(s, e, chunks):
    """整句的起止时间 → 每一条的 (起, 止)，按中文宽度占比分。"""
    tot = sum(c[2] for c in chunks) or 1.0
    out, acc = [], 0.0
    for c in chunks:
        a = s + (e - s) * acc / tot
        acc += c[2]
        out.append((a, s + (e - s) * acc / tot))
    return out


def display_windows(items):
    """items = [(s, e)]，按时间排好 → 每条的显示区间 [(a, b)]：开始前 LEAD、结束后 LAG，下一条开始前 LEAD 收掉，不叠。"""
    out = []
    for i, (s, e) in enumerate(items):
        a, b = s - LEAD, e + LAG
        if i + 1 < len(items):
            b = min(b, items[i + 1][0] - LEAD - 0.02)
        out.append((a, max(b, a + 0.3)))
    return out


# ---------------------------------------------------------------- 输出
def ts_ass(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def ts_srt(t):
    ms = round(max(0.0, t) * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def esc_ass(s):
    return s.replace("{", "(").replace("}", ")")


def ass_header(zh_font="NSC800", en_font="NSC600", extra_styles=""):
    """1920×1080 的 ASS 头：ZH / EN 两个样式（白边向外 5 px / 3 px，居中对齐 \\an5，位置由每条 Dialogue 的 \\pos 给）。"""
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ZH,{zh_font},{ZH_PX},{INK},&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,5,0,5,0,0,0,1
Style: EN,{en_font},{EN_PX},{GREY},&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1
{extra_styles}
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_events(a, b, zh_text, en_text, cx=960):
    """一条字幕 → 两行 Dialogue（中文、英文）。zh_text 可以带 ASS 覆盖标签（比如橙色标签），不要再转义。"""
    return [f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},ZH,,0,0,0,,{{\\an5\\pos({cx},{ZH_CY})}}{zh_text}",
            f"Dialogue: 0,{ts_ass(a)},{ts_ass(b)},EN,,0,0,0,,{{\\an5\\pos({cx},{EN_CY})}}{esc_ass(en_text)}"]


def write_srts(path_prefix, rows):
    """rows = [(a, b, zh, en)] → <prefix>_双语字幕.srt / _中文字幕.srt / _英文字幕.srt（路径前缀由调用方定，比如 .../成片）。"""
    out = {"both": [], "zh": [], "en": []}
    for i, (a, b, zh, en) in enumerate(rows, 1):
        head = f"{i}\n{ts_srt(a)} --> {ts_srt(b)}\n"
        out["both"].append(head + zh + "\n" + en + "\n")
        out["zh"].append(head + zh + "\n")
        out["en"].append(head + en + "\n")
    for key, name in (("both", "双语字幕"), ("zh", "中文字幕"), ("en", "英文字幕")):
        with open(f"{path_prefix}_{name}.srt", "w", encoding="utf-8") as f:
            f.write("\n".join(out[key]))
