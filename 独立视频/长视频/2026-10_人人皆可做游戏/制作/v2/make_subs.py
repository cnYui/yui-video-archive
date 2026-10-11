# -*- coding: utf-8 -*-
"""make_subs.py —— 字幕：subs_src.py 的每一条按口播对位 → 成片时间 → 拆成 ≤ 28 字 / ≤ 90 字符的条 → 2340 宽的 ASS + 三份 SRT + 核对表。
  python make_subs.py          → 字幕.ass、成片_{双语,中文,英文}字幕.srt、字幕核对表.md（都在 制作/ 下）
中英双语标准（项目统一）：中文 52 px 一行 + 英文 30 px 一行，y 922 起；每条开始前 0.1 s 显示、结束后 0.45 s 收掉，不叠。
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, r"D:\大疆\Way to AGI\skill\way-to-agi-episode\scripts")

import bilingual_std as B  # noqa: E402
import voice  # noqa: E402
from subs_src import UNITS  # noqa: E402

CX = 1170                       # 2340 宽画布的中线
VOICED = -42.0


def onset(db, t):
    """token 的开始时间不可靠（Whisper 会把停顿算进上一个字）：
    t 往后 0.05 秒还是静音，就找下一个“静音 → 有声”的起点；否则就是这个时间。"""
    i = int(t * 100)
    if db[min(len(db) - 1, i + 5)] > VOICED:
        return t
    for k in range(i, min(len(db) - 3, i + 250)):
        if db[k] > VOICED and db[k + 1] > VOICED and db[k + 2] > VOICED:
            return k / 100
    return t


def last_voiced(db, t_limit):
    i = min(len(db) - 1, int(t_limit * 100))
    while i > 0 and db[i] < VOICED:
        i -= 1
    return (i + 1) / 100


def build():
    tl = voice.timeline()
    envs = {c: voice.load_env(c) for c in voice.CLIPS}
    kept_end = {c: max(p["src_out"] for p in tl if p["clip"] == c) for c in voice.CLIPS}
    rows = []
    prev: dict = {}
    for clip, anchor, zh, en, note in UNITS:
        after = prev.get(clip, -1.0) + 0.02
        s = voice.find_phrase(clip, anchor, after)
        if s is None:
            raise SystemExit("找不到锚点：%s %r（在 %.2f 之后）" % (clip, anchor, after))
        prev[clip] = s
        rows.append({"clip": clip, "s_tok": s, "zh": zh, "en": en, "note": note})
    # 结束 = 同一素材里下一条开始之前最后有声音的那一刻
    for i, r in enumerate(rows):
        db = envs[r["clip"]]
        r["s"] = onset(db, r["s_tok"])
        nxt = next((q for q in rows[i + 1:] if q["clip"] == r["clip"]), None)
        limit = (nxt["s_tok"] - 0.03) if nxt else kept_end[r["clip"]]
        r["e"] = max(r["s"] + 0.3, last_voiced(db, limit) + 0.04)
        r["a"] = voice.out_time(tl, r["clip"], r["s"])
        r["b"] = voice.out_time(tl, r["clip"], r["e"])
    rows.sort(key=lambda r: r["a"])
    # 拆成不超限的条
    out = []
    for r in rows:
        zu, el = B.zh_units(r["zh"]), len(r["en"])
        if zu > B.ZH_MAX or el > B.EN_MAX:
            chunks = B.split_pair_aligned(r["zh"], r["en"])
        else:
            chunks = [(r["zh"], r["en"], zu)]
        for (z, e, _), (a, b) in zip(chunks, B.chunk_times(r["a"], r["b"], chunks)):
            out.append({"a": a, "b": b, "zh": z, "en": e, "note": r["note"], "clip": r["clip"]})
    wins = B.display_windows([(o["a"], o["b"]) for o in out])
    for o, (a, b) in zip(out, wins):
        o["da"], o["db"] = a, b
    return out


def write_all(out, total):
    head = B.ass_header().replace("PlayResX: 1920", "PlayResX: 2340")
    lines = [head]
    for o in out:
        lines += B.ass_events(o["da"], o["db"], o["zh"], o["en"], cx=CX)
    (ROOT / "字幕.ass").write_text("\n".join(lines) + "\n", encoding="utf-8")
    B.write_srts(str(ROOT / "正片"), [(o["da"], o["db"], o["zh"], o["en"]) for o in out])
    # 核对表
    md = ["# 字幕核对表（长视频《欢迎来到 人人皆可做游戏的 时代》）", "",
          "共 %d 条；时间是成片秒（不含片头）。中文 = 他说的话（ASR 听错的字已改），英文 = 翻译。" % len(out), "",
          "## 要请你确认的词（ASR 听不准、我按上下文写的）", ""]
    seen = set()
    for o in out:
        if o["note"] and o["note"] not in seen:
            seen.add(o["note"])
            md.append("- %s　→ %s" % (o["note"], o["zh"]))
    md += ["", "## 逐条", "", "| # | 时间 | 中文 | 英文 |", "|---|---|---|---|"]
    for i, o in enumerate(out, 1):
        md.append("| %d | %d:%04.1f–%d:%04.1f | %s | %s |" % (i, o["a"] // 60, o["a"] % 60, o["b"] // 60, o["b"] % 60, o["zh"], o["en"]))
    (ROOT / "字幕核对表.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def qa(out):
    bad = 0
    for i, o in enumerate(out, 1):
        d = o["b"] - o["a"]
        zu = B.zh_units(o["zh"])
        if zu > B.ZH_MAX or len(o["en"]) > B.EN_MAX:
            print("超限", i, round(zu, 1), len(o["en"]), o["zh"])
            bad += 1
        if d < 0.5 or zu / max(d, 0.1) > 9.5:
            print("太快/太短 #%d  %.2f s  %.1f 字  %s" % (i, d, zu, o["zh"]))
    print("条数", len(out), "问题", bad)


if __name__ == "__main__":
    out = build()
    qa(out)
    write_all(out, voice.total(voice.timeline()))
    print("ok", len(out))
