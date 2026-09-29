"""Build 制作/timeline.json — the single source of timing for engine, subtitles, chapter bar and audio mix.

  python build_timeline.py <episode_dir> [--series D:/大疆/AI科普]

Inputs
  episode.json                  chapters (bar titles), backgrounds, questions, bg_alpha / bg_blur …
  台本/script_data.py            scenes, rows, subtitle text, visual notes with 【动作：xxx】
  制作/voice/durations.json      optional {segment_id: seconds} measured from the TTS clips (else estimate)
  制作/voice/alignment.json      optional {segment_id: [{text, start, end}]} line timing inside each clip
  片头片尾/intro|outro/index.html window.DURATION (fallback 3.8 s / 4.8 s)
Outputs
  制作/timeline.json             see references/pipeline-contract.md §6 (never edit by hand)
  制作/chapters_bilibili.txt     "m:ss 章节名" lines for the Bilibili chapter field

Times in segments / gaps / scenes / actions / toc are MAIN-BODY time (0 = first frame after the intro);
times in chapters are WHOLE-VIDEO time (intro + main + outro) so the burned-in bar matches the player.
Subtitles: split at punctuation, never inside an English word or path, each line <= 20 CJK widths (only a single
unbreakable word / URL may be wider), 避头尾 (a line never starts with ”’）》」』】、，。！？；：… and never ends with
“‘（《「『【 -- they stick to their neighbour), orphan fragments merged or re-split, then retimed on the ASR
alignment. A clause wider than 20 is cut at its best breaks (after punctuation, where Chinese meets English, after
的/了, between English words; not inside “…” / （…） if avoidable). Afterwards run mix_audio.py (it writes `mouth`);
when voice placement, chapter starts and tick moments are unchanged (e.g. only titles / backgrounds /
terms edited) the old `mouth` is kept and build/mix.wav stays valid — the script says which case it is.

Action notes (contract §4 · 动作 v2): 【动作：抬手】 at the word's default place (段首, or 段尾 for 摊手 / 竖拇指 /
点头 / 好耶 / 叉腰@末尾 …), 【动作：开心@末尾】 at the row end, 【动作：数一@第一】 from the moment that phrase is spoken,
【动作：看右边@整段】 over the whole row, 【动作：摇头+认真】 two at once, 【动作：不动】 = no auto gestures in this row.
Explicit actions that would start during the opening walk-in are moved to its end (printed); hand / head / sticker
actions also wait 0.25 s after it (she stops before she waves). 【动作：开心@末尾】 (a whole-row expression written with
an explicit @) only takes its 2 s at that place. Afterwards the big actions
(epcommon.BIG_WORDS) are checked for the >= 15 s spacing on the real times. The auto layer (small gestures, nods, looks)
is NOT written here: the engine plans it itself from episode.auto_gestures (copied into timeline.episode).
"""
import argparse
import copy
import json
import math
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import epcommon as C  # noqa: E402

FPS = 30
MAX_LINE = 20          # max display width (CJK units) per subtitle line (only one unbreakable word / path may exceed it)
ORPHAN = 5             # a line narrower than this is merged into its neighbour (or the pair is re-split)

# 避头尾 (kinsoku): these never start a line -- they stay at the end of the line before ...
NO_START = set("”’）》」』】〕〉、，。！？；：…%‰°℃)]}!?,.;:")
# ... and these never end a line -- they move to the start of the next one
NO_END = set("“‘（《「『【〔〈([{#$¥￥")
CLAUSE_END = set("，。？！：；、")
LINE_TRIM = "，、；："   # dropped at the end of a displayed line
PARTICLE = set("的了着过地得")
OPENERS, CLOSERS = set("“‘（《「『【〔〈([{"), set("”’）》」』】〕〉)]}")   # a break inside a pair costs extra
# orange subtitle terms are never broken across two lines (a split term would lose its colour): the engine's
# built-in list (== core.js ENG.TERMS) + episode.json "terms"; main() fills KEEP. Same word-edge rule as core.js:
# an English / digit edge of a term must not touch another letter / digit (nor _ - / . before it, _ - after it).
ENGINE_TERMS = ["API Key", "API key", "API", "Token", "token", "JSON", "HTTP", "SSE", "LLM", "Prompt", "prompt"]
KEEP = []
ATOM_RE = re.compile(r"[A-Za-z0-9_./:\-]+ ?|.")


# ---------------------------------------------------------------- subtitles (episode-1 v3 rules + 避头尾)
def width(s):
    """Display width in CJK-character units (ASCII letters/digits are about half as wide)."""
    return sum(0.55 if ord(c) < 128 else 1.0 for c in s)


def _shown(s):
    """a line as it is displayed: no trailing ，、；： or spaces"""
    return s.strip().rstrip(LINE_TRIM).strip()


def dwidth(s):
    """display width of a finished line (trailing ，、；： are dropped, see split_lines)"""
    return width(_shown(s))


def set_terms(terms):
    """phrases split_lines keeps on one line: ENGINE_TERMS + `terms` (episode.json), longest first"""
    KEEP[:] = sorted({str(t) for t in list(ENGINE_TERMS) + list(terms or []) if len(str(t)) > 1}, key=lambda t: (-len(t), t))


def _term_at(s, i):
    """the longest KEEP term that starts at s[i] with valid word edges, or None"""
    for t in KEEP:
        j = i + len(t)
        if not s.startswith(t, i):
            continue
        if _is_ascii_word(t[0]) and i > 0 and (_is_ascii_word(s[i - 1]) or s[i - 1] in "_-/."):
            continue
        if _is_ascii_word(t[-1]) and j < len(s) and (_is_ascii_word(s[j]) or s[j] in "_-"):
            continue
        return t
    return None


def _atoms(clause):
    """Break a clause into unbreakable pieces: single CJK chars, whole ASCII words (with trailing space), and whole
    orange terms (KEEP, e.g. 'Artificial General Intelligence', '基于人类反馈的强化学习')."""
    out, i = [], 0
    while i < len(clause):
        t = _term_at(clause, i) if KEEP else None
        if t:
            j = i + len(t)
            if j < len(clause) and clause[j] == " " and t[-1].isascii():
                j += 1                            # like an English word: the trailing space goes with it
            out.append(clause[i:j])
            i = j
            continue
        m = ATOM_RE.match(clause, i)
        out.append(m.group(0))
        i = m.end()
    return out


def _units(s):
    """Atoms glued by the kinsoku rules: a NO_START mark joins the unit before it (”）。、… never open a line),
    a NO_END mark joins the unit after it (“（《 never close one). A line break can only fall between units."""
    units, lead = [], ""
    for a in _atoms(s):
        if a in NO_END:
            lead += a
        elif (a in NO_START or (a == "—" and units[-1:] and units[-1].endswith("—"))) and units and not lead:
            units[-1] += a                    # (and a —— dash is never cut in two)
        else:
            units.append(lead + a)
            lead = ""
    if lead:                                  # text ends with an opening mark: it stays on the last line
        if units:
            units[-1] += lead
        else:
            units.append(lead)
    return units


def _clauses(text):
    """Split after clause punctuation (，。？！：；、) together with the closing marks that follow it, so
    '吗？”一句话' becomes '吗？”' | '一句话' (never '吗？' | '”一句话')."""
    out, cur, i = [], "", 0
    while i < len(text):
        ch = text[i]
        cur += ch
        i += 1
        if ch in CLAUSE_END:
            while i < len(text) and text[i] in NO_START:
                cur += text[i]
                i += 1
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return [c for c in out if c.strip()]


def _is_ascii_word(ch):
    return ch.isascii() and ch.isalnum()


def _rejoins(line, nxt):
    """True when the engine would glue `nxt` onto `line` on screen: core.js buildSubs joins a line of >= 18
    characters that ends in [A-Za-z0-9_.-] with a next line that starts with one (it re-joins the words episode 1's
    old builder hard-wrapped) -- without a space and without a dropped ，. So split_lines never breaks there."""
    a, b = line.strip(), nxt.strip()
    return len(a) >= 18 and bool(re.search(r"[A-Za-z0-9_.\-]$", a)) and bool(re.match(r"[A-Za-z0-9_.\-]", b))


def _break_cost(left, right):
    """How bad a break between unit `left` and unit `right` is: 0 after clause punctuation or …… (and the closing
    marks after it), 1 after a closing quote / bracket or where Chinese meets English, 1.5 after 的/了… or between
    two English words, 4 inside a run of Chinese characters (may cut a word; there is no word segmentation here)."""
    a, b = left.rstrip(), right.lstrip()
    if not a or not b:                        # next to a lone space (e.g. between Chinese and English)
        return 1.0
    k = len(a)
    while k and a[k - 1] in NO_START and a[k - 1] not in CLAUSE_END and a[k - 1] != "…":
        k -= 1
    if k and (a[k - 1] in CLAUSE_END or a[k - 1] == "…"):
        return 0.0
    if k < len(a):
        return 1.0
    x, y = a[-1], b[0]
    if _is_ascii_word(x) != _is_ascii_word(y):
        return 1.0
    if x in PARTICLE:
        return 1.5
    if _is_ascii_word(x) and _is_ascii_word(y):
        return 1.5
    return 4.0


def _best_lines(units, k):
    """Split units into exactly k lines (each <= MAX_LINE unless it is a single unit) with the lowest
    break cost (+2 inside a “…” / （…） pair) + 0.3 x distance from an even split + 6 per orphan (< ORPHAN).
    Lines keep their spaces (split_lines trims them for display). None when impossible."""
    n = len(units)
    if k < 1 or k > n:
        return None
    mean = width("".join(units)) / k
    depth, d = [0], 0                         # quote / bracket depth at each boundary
    for u in units:
        for ch in u:
            d = d + 1 if ch in OPENERS else max(0, d - 1) if ch in CLOSERS else d
        depth.append(d)
    inf = float("inf")
    best = [[(inf, -1)] * (k + 1) for _ in range(n + 1)]
    best[0][0] = (0.0, -1)
    for j in range(1, n + 1):
        for m in range(1, min(k, j) + 1):
            cand = (inf, -1)
            for i in range(j - 1, m - 2, -1):
                w = dwidth("".join(units[i:j]))
                if w > MAX_LINE and j - i > 1:
                    break                         # longer lines only get wider
                prev = best[i][m - 1][0]
                if prev == inf:
                    continue
                if j < n and _rejoins(_shown("".join(units[i:j])), units[j]):
                    continue                      # the engine would glue the next line back on (see _rejoins)
                c = prev + 0.3 * abs(w - mean) + (6.0 if w < ORPHAN else 0.0)
                if i:
                    c += _break_cost(units[i - 1], units[i]) + (2.0 if depth[i] else 0.0)
                if c < cand[0]:
                    cand = (c, i)
            best[j][m] = cand
    if best[n][k][0] == inf:
        return None
    lines, j = [], n
    for m in range(k, 0, -1):
        i = best[j][m][1]
        lines.append("".join(units[i:j]))
        j = i
    return lines[::-1]


def _split_wide(s, parts=None):
    """A piece wider than MAX_LINE -> the fewest lines that fit, at the best breaks (kinsoku-safe, never inside an
    English word or path). parts=2: the best two-line split of s whatever its width (for re-balancing orphans)."""
    units = _units(s)
    if parts:
        return _best_lines(units, parts)
    if dwidth(s) <= MAX_LINE or len(units) < 2:
        return [s]
    k = max(2, math.ceil(dwidth(s) / MAX_LINE))
    while k <= len(units):
        lines = _best_lines(units, k)
        if lines:
            return lines
        k += 1
    return [s]


def split_lines(text):
    """Split a subtitle into display lines: break at punctuation first, never inside an English word or path,
    keep each line <= MAX_LINE wide, avoid orphan fragments of just two or three characters, and follow the
    避头尾 rules: ”’）》」』】、，。！？；：… never start a line (they stay at the end of the line before),
    “‘（《「『【 never end one (they go to the start of the next line)."""
    # 1) clauses; one wider than the limit is split into balanced lines at its best breaks
    pieces = []                 # (text, starts_new_line)
    for c in _clauses(text):
        sub = _split_wide(c)
        for x in sub:
            pieces.append((x, len(sub) > 1))  # each part of a split clause opens a line (the last one may take more)
    # 2) greedily join pieces into lines
    lines, cur = [], ""
    for p, fresh in pieces:
        if cur and (fresh or width(cur) + width(p) > MAX_LINE):
            lines.append(cur)
            cur = p
        else:
            cur += p
    if cur:
        lines.append(cur)
    # 3) orphans (< ORPHAN wide, measured as before): merge into the neighbour when the result fits, else re-split
    #    the pair into two lines when that leaves no orphan
    merged = []
    for k, ln in enumerate(lines):
        if merged and (width(ln) < ORPHAN or width(merged[-1]) < ORPHAN):
            both = merged[-1] + ln
            nxt = lines[k + 1] if k + 1 < len(lines) else ""
            if dwidth(both) <= MAX_LINE and not (nxt and _rejoins(_shown(both), nxt)):
                merged[-1] = both
                continue
            pair = _split_wide(both, parts=2)
            if pair and min(width(x.strip()) for x in pair) >= ORPHAN and not (nxt and _rejoins(_shown(pair[-1]), nxt)):
                merged[-1:] = pair
                continue
        merged.append(ln)
    raw = [ln for ln in merged if _shown(ln)]
    out = [_shown(ln) for ln in raw]
    for i in range(len(out) - 1):             # a dropped line-end ，/：would let the engine glue two lines (_rejoins)
        if _rejoins(out[i], out[i + 1]):
            out[i] = raw[i].strip()
    return out


def _norm(s):
    return re.sub(r'[\s，。？！：；、“”"\'（）()·—\-]', '', s)


def retime_lines(text, old_lines, seg_start, seg_dur):
    """Time freshly split lines from an older aligned split: interpolate time per normalised character
    inside each old line, then read off the new line boundaries."""
    marks = []                                   # (char_position, time) knots
    pos = 0
    for ol in old_lines:
        n = len(_norm(ol["text"]))
        marks.append((pos, ol["start"]))
        pos += n
        marks.append((pos, ol["end"]))
    total = pos or 1

    def t_at(p):
        for (p0, t0), (p1, t1) in zip(marks, marks[1:]):
            if p0 <= p <= p1:
                return t0 if p1 == p0 else t0 + (t1 - t0) * (p - p0) / (p1 - p0)
        return marks[-1][1]

    new = split_lines(text)
    out, pos = [], 0
    for i, ln in enumerate(new):
        n = len(_norm(ln))
        a = 0.0 if i == 0 else t_at(min(pos, total))
        b = seg_dur if i == len(new) - 1 else t_at(min(pos + n, total))
        out.append(dict(text=ln, start=round(seg_start + a, 3), end=round(seg_start + max(b, a + 0.3), 3)))
        pos += n
    for i in range(1, len(out)):
        out[i]["start"] = out[i - 1]["end"]
    return out


def proportional_lines(text, start, dur):
    parts = split_lines(text)
    total = sum(len(p) for p in parts) or 1
    lines, lt = [], start
    for p in parts:
        ld = dur * len(p) / total
        lines.append(dict(text=p, start=round(lt, 3), end=round(lt + ld, 3)))
        lt += ld
    return lines


def phrase_time(lines, phrase):
    """Moment `phrase` starts being spoken, interpolated inside the subtitle line that contains it."""
    acc, spans = "", []
    for ln in lines:
        spans.append((len(acc), len(acc) + len(ln["text"]), ln))
        acc += ln["text"]
    i = acc.find(phrase)
    if i < 0:
        return None
    for a, b, ln in spans:
        if a <= i < b:
            return ln["start"] + (ln["end"] - ln["start"]) * (i - a) / max(1, b - a)
    return None


# ---------------------------------------------------------------- actions
def schedule(acts, a, b, lines, where, warns):
    """Turn parsed 【动作】 notes of one row [a, b] into timeline actions (main time)."""
    out = []
    for act in acts:
        if act.get("anchor") == "whole":   # 整段 words without @, or any word written @整段
            s, e = a, b
            if act.get("max") and e - s > act["max"]:
                e = s + act["max"]          # 合手：整段，最长 6 s
        else:                               # (开心@末尾 / 认真@短语: a whole-row expression anchored explicitly -> dur)
            d = act.get("dur") or act.get("max") or 1.5
            anchor = act["anchor"]
            if anchor == "end":
                s = max(a, b - d)
            elif anchor == "start":
                s = a
            else:
                t = phrase_time(lines, anchor) if lines else None
                if t is None:
                    warns.append(f"{where}：【动作：{act['word']}@{anchor}】找不到短语「{anchor}」，改为段首")
                    t = a
                s = t
            e = min(b, s + d) if act.get("clip") else s + d
            if e - s < 0.3:
                e = s + min(d, 0.3)
            if not act.get("clip") and e > b + 0.05:
                warns.append(f"{where}：{act['word']}（{d} s）比这一行长，会延续到 {e:.2f}s（行尾 {b:.2f}s）")
        out.append(dict(type=act["type"], name=act["name"], start=round(s, 3), end=round(e, 3)))
    return out


def check_overlaps(timeline_actions, warns):
    """Same-channel overlaps (body, eyes, sprite = sticker / anim, head, fx) and head-over-body."""
    chan = {"body": "body", "expr": "eyes", "pose": "sprite", "anim": "sprite", "head": "head", "fx": "fx"}
    by = {}
    for where, a in timeline_actions:
        if a["type"] in chan:              # "auto" (不动) is a switch, not a channel
            by.setdefault(chan[a["type"]], []).append((a["start"], a["end"], where, a["name"]))
    for ch, lst in by.items():
        lst.sort()
        for (s0, e0, w0, n0), (s1, e1, w1, n1) in zip(lst, lst[1:]):
            if s1 < e0 - 0.01:
                warns.append(f"动作重叠（{ch}）：{w0} {n0} {s0:.2f}–{e0:.2f}s 和 {w1} {n1} {s1:.2f}–{e1:.2f}s")
    for s0, e0, w0, n0 in by.get("head", []):
        for s1, e1, w1, n1 in by.get("body", []) + by.get("sprite", []):
            if s0 < e1 - 0.01 and s1 < e0 - 0.01:
                warns.append(f"头部动作 {w0} {n0} {s0:.2f}–{e0:.2f}s 和 {w1} {n1} 重叠：头部动作只在手放下时播放，会被盖掉")


WALK_SETTLE = 0.25    # s: a gesture starts no earlier than this after the opening walk-in (QA #18: 走入后停一下再挥手)


def clear_walk_in(pending, walk_end, warns):
    """Explicit actions that start during the opening walk-in (which always wins) are moved to its end; hand / head /
    sticker actions also wait WALK_SETTLE s after it, so she stops before she waves."""
    if walk_end <= 0:
        return
    for row, _acts, _lines, where in pending:
        for a in row["actions"]:
            if a["name"] == "walk" or a["type"] == "auto":
                continue
            settle = WALK_SETTLE if a["type"] in ("body", "head", "pose") else 0.05
            if a["start"] >= walk_end + settle - 0.001 or (a["type"] not in ("body", "head", "pose")
                                                          and a["start"] >= walk_end - 0.001):
                continue
            d = a["end"] - a["start"]
            s = round(walk_end + settle, 3)
            e = round(s + d, 3)                 # keeps its length (it may run into the next row)
            if a["start"] < walk_end - 0.001:
                warns.append(f"{where}：{a['type']} {a['name']} 原来 {a['start']:.2f}s 开始，和开场走入重叠，已推到走入结束后 {s:.2f}s")
            a["start"], a["end"] = s, e


def check_big_spacing(all_actions, warns):
    """大动作 (epcommon.BIG_WORDS) on the real times: at most ACTION_LIMITS big_total, >= big_spacing s apart."""
    lim = getattr(C, "ACTION_LIMITS", None)
    if not lim:
        return
    big_names = {(C.ACTIONS[w]["type"], C.ACTIONS[w]["name"]): w for w in getattr(C, "BIG_WORDS", [])}
    counts = {w for w in C.ACTIONS if C.ACTIONS[w].get("count")}
    big = sorted((a["start"], big_names[(a["type"], a["name"])], where) for where, a in all_actions
                 if (a["type"], a["name"]) in big_names)
    if len(big) > lim["big_total"]:
        warns.append(f"大动作一共 {len(big)} 个，全片上限 {lim['big_total']}")
    for (t0, n0, w0), (t1, n1, w1) in zip(big, big[1:]):
        if t1 - t0 < lim["big_spacing"] and not (n0 in counts and n1 in counts):
            warns.append(f"大动作太近：{w0} {n0}（{C.mmss(t0)}）和 {w1} {n1}（{C.mmss(t1)}）相隔 {t1 - t0:.1f}s，"
                         f"建议 ≥ {lim['big_spacing']:.0f}s")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    C.add_common(ap)
    args = ap.parse_args()
    p = C.Paths(args.episode_dir, args.series)
    ep = C.load_episode(p)
    canvas = C.canvas_of(ep)              # stops on a canvas that cannot be rendered (height 1080, even width >= 1920)
    set_terms(ep.get("terms"))            # subtitle lines never break inside an orange term
    ns = C.load_script(p)
    scenes_src = C.walk_script(ns["SCENES"])
    durations = C.load_json(p.durations, {})
    alignment = C.load_json(p.alignment, {})
    intro, outro = C.pack_durations(p)
    warns = []

    t = 0.0
    segments, gaps, scenes, pending = [], [], [], []
    for sc in scenes_src:
        start = t
        for r in sc["rows"]:
            acts, w = C.parse_actions(r["visual"])
            warns += [f"{sc['id']}：{x}" for x in w]
            if r["kind"] == "gap":
                g = dict(scene=sc["id"], start=round(t, 3), end=round(t + r["dur"], 3), visual=r["visual"], actions=[])
                gaps.append(g)
                pending.append((g, acts, None, f"{sc['id']} 停顿@{t:.1f}s"))
                t += r["dur"]
                continue
            sid = r["id"]
            dur = float(durations.get(sid, C.est_seconds(r["tts"])))
            if sid in alignment:
                lines = retime_lines(r["text"], alignment[sid], t, dur)
            else:
                lines = proportional_lines(r["text"], t, dur)
            s = dict(id=sid, scene=sc["id"], start=round(t, 3), end=round(t + dur, 3), text=r["text"], tts=r["tts"],
                     visual=r["visual"], pose="reach" if any(a["name"] == "reach" for a in acts) else "idle",
                     lines=lines, measured=sid in durations, actions=[])
            segments.append(s)
            pending.append((s, acts, lines, sid))
            t += dur + C.SEG_GAP
        scenes.append(dict(id=sc["id"], title=sc["title"], start=round(start, 3), end=round(t, 3), notes=sc["char"]))
    main_dur = round(t, 3)
    total = round(intro + main_dur + outro, 3)

    # actions (after all times are known)
    for row, acts, lines, where in pending:
        row["actions"] = schedule(acts, row["start"], row["end"], lines, where, warns)
    first_walk = next((a for row, *_ in pending for a in row["actions"] if a["name"] == "walk" and a["start"] <= 0.01), None)
    walk_in = dict(start=0.0, end=first_walk["end"]) if first_walk else dict(start=0.0, end=0.0)
    clear_walk_in(pending, walk_in["end"], warns)
    all_actions = []
    for row, acts, lines, where in pending:
        for a in row["actions"]:
            a["end"] = round(min(a["end"], main_dur), 3)
            all_actions.append((where, a))
    check_overlaps(all_actions, warns)
    check_big_spacing(all_actions, warns)

    # chapters, backgrounds, episode block
    ids = [s["id"] for s in scenes]
    titles = ep.get("chapters", {})
    for sid in ids:
        if sid not in titles:
            warns.append(f"episode.json chapters 没写 {sid}，进度条用场景名")
    bg_files, _auto = C.fill_backgrounds(p, ep, ids, warns)
    bg_rel = {sid: (C.rel_from_engine(p, p.bg_library / f) if f else None) for sid, f in bg_files.items()}
    for s in scenes:
        s["bg"] = bg_rel[s["id"]]
        s["chapter"] = titles.get(s["id"], s["title"])
    chapters = []
    for i, s in enumerate(scenes):
        c_start = 0.0 if i == 0 else intro + s["start"]
        c_end = total if i == len(scenes) - 1 else intro + s["end"]
        chapters.append(dict(id=s["id"], title=s["chapter"], start=round(c_start, 3), end=round(c_end, 3)))

    episode = {k: copy.deepcopy(v) for k, v in ep.items() if not k.startswith("_")}
    episode["backgrounds"] = bg_rel
    episode["background_files"] = bg_files
    if "canvas" in ep:                    # frame size [W, H] (checked; the engine / render.py read it from here).
        episode["canvas"] = list(canvas)  # No "canvas" in episode.json = 1920x1080, and the timeline stays as before.

    # table of contents helper (for the tick sound in mix_audio.py; the engine derives the same moments
    # itself): when the TOC flies in and when each question is ticked
    toc = None
    sc_by = {s["id"]: s for s in scenes}
    if ep.get("questions"):
        qs = ep.get("question_scene", "S02")
        q_segs = [s for s in segments if s["scene"] == qs]
        if q_segs:
            last = q_segs[-1]
            t_in = max(last["start"] + 0.8, last["end"] - 0.75)
        else:
            first = next((sc_by[x] for x in (ep["questions"][0].get("scenes") or []) if x in sc_by), None)
            warns.append(f"question_scene {qs} 没有台词，目录在第一题的章节开始前出现")
            t_in = max(0.0, first["start"] - 0.4) if first else 0.0
        items = []
        for q in ep["questions"]:
            qsc = [sc_by[x] for x in q.get("scenes", []) if x in sc_by]
            for x in q.get("scenes", []):
                if x not in sc_by:
                    warns.append(f"questions「{q.get('text')}」的章节 {x} 不存在")
            if not qsc:
                items.append(dict(text=q.get("text", ""), scenes=q.get("scenes", []), done=None))
                continue
            # ticked when the talking of its last scene is over (engine core.js endTalk): the start of the
            # scene's closing gap, else scene end - 0.4 s
            lastsc = max(qsc, key=lambda s: s["start"])
            src_rows = next(x for x in scenes_src if x["id"] == lastsc["id"])["rows"]
            if src_rows and src_rows[-1]["kind"] == "gap":
                done = [g for g in gaps if g["scene"] == lastsc["id"]][-1]["start"]
            else:
                done = lastsc["end"] - 0.4
            items.append(dict(text=q.get("text", ""), scenes=q.get("scenes", []), done=round(done, 3)))
        toc = {"in": round(t_in, 3), "items": items}

    timeline = dict(fps=FPS, intro=intro, outro=outro, main_duration=main_dur, total_duration=total,
                    episode=episode, chapters=chapters, scenes=scenes, segments=segments, gaps=gaps,
                    walk_in=walk_in, toc=toc)
    old = C.load_json(p.timeline)
    keep_mix = bool(old and old.get("mouth") and C.mix_signature(old) == C.mix_signature(timeline))
    if keep_mix:                      # voice placement, chapter starts and ticks unchanged: mouth + mix still valid
        timeline["mouth"] = old["mouth"]
    C.write_json(p.timeline, timeline)
    chap_txt = "\n".join(f"{C.mmss(c['start'])} {c['title']}" for c in chapters)
    (p.prod / "chapters_bilibili.txt").write_text(chap_txt + "\n", encoding="utf-8")

    stale = sorted(set(durations) - {s["id"] for s in segments})
    if stale:
        warns.append(f"durations.json 里有台本中没有的段 {stale[:6]}：台本改过，要重新配音 / segment_audio")
    measured = sum(1 for s in segments if s["measured"])
    if measured < len(segments):
        warns.append(f"{len(segments) - measured} 段还没有实测时长（用估算），配音后要重跑")
    n_act = len(all_actions)
    kinds = {}
    for _, a in all_actions:
        kinds[a["type"]] = kinds.get(a["type"], 0) + 1
    ag = ep.get("auto_gestures", None)
    auto_txt = ("off" if ag is False else ("on " + json.dumps(ag, ensure_ascii=False) if isinstance(ag, dict) else "on"))
    lo, hi = ep.get("target_minutes", [5, 7])
    print(f"main={main_dur:.1f}s total={total:.1f}s ({C.mmss(total)}) segments={len(segments)} measured={measured} "
          f"gaps={len(gaps)} actions={n_act} {kinds} auto_gestures={auto_txt} "
          f"canvas={canvas[0]}x{canvas[1]}{'' if 'canvas' in ep else ' (episode.json 没写 canvas，按默认)'}")
    if not lo * 60 <= total <= hi * 60:
        warns.append(f"总长 {C.mmss(total)} 不在目标 {lo}–{hi} 分钟内")
    print(chap_txt)
    if keep_mix:
        print(f"-> {p.timeline}\n配音位置、章节起点、打勾时刻都没变：保留原来的 mouth，build/mix.wav 仍然有效")
    else:
        print(f"-> {p.timeline}\n下一步：mix_audio.py（写入 mouth 和混音）")
    for w in warns:
        print("[提醒]", w)


if __name__ == "__main__":
    main()
