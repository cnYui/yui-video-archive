"""中英双语字幕（项目统一标准）的共用部分：《原LAI如此》（build_timeline.py、build_script.py）和《AI每日日报》（bilingual_subs.py）都用这一份。

标准 = `D:/大疆/Way to AGI/skill/way-to-agi-episode/references/subtitles.md`「中英双语」，代码 `scripts/bilingual_std.py`
（这里直接 import，不另抄一份，标准改了两档节目跟着变）：
  - 中文一行 52 px（Noto Sans SC 800，墨黑 #1B1B1F + 白边）在上，英文一行 30 px（600，灰 #4B5563 + 白边）在下，居中；
  - 一条中文 ≤ 约 28 字、英文 ≤ 约 90 字符，各一行不换行；放不下就拆条（split_pair_aligned：中英文一起找断点），
    拆得不顺的句子手动写 cuts（[[中文锚点, 英文锚点], …]：中文在这段文字之后断、英文在这段文字之后断，按出现的先后找）；
  - 每条开始前 0.1 s 显示到结束后 0.45 s，不和下一条重叠；
  - 导出三份 SRT：双语（中文在上）/ 中文 / 英文（B.write_srts）。
两档节目画面底部都有全宽进度条，字幕带从标准的 y 922 上移到 y 900（引擎 #subs.bi），一行最宽 1560 px（不碰左下角的讲解员）。

用户 2026-10-02：日报“改成双语，按统一标准来”，同一天“原LAI如此也改成双语”。

提供：
  check_pair(where, zh, en, cuts)   → (errs, warns)：缺英文、英文里有汉字 / 全角标点、中文里的英文名在英文里没原样出现、
                                      拆完还放不下一行（errs）；数字在英文里找不到、英文略超 90（warns）
  split(zh, en, cuts)               → [(中文段, 英文段, 中文宽度)]
  seg_subs(seg, en, cuts)           → 一段时间轴 segment 的字幕条 [{zh, en, s, e}]（按 seg.lines 的逐字时刻计时），是否逐字对上
  set_windows(subs)                 → 给全片按时间排好的字幕条加显示区间 a / b
"""
import re
import sys
from pathlib import Path

STD_DIR = Path(r"D:/大疆/Way to AGI/skill/way-to-agi-episode/scripts")
if str(STD_DIR) not in sys.path:
    sys.path.insert(0, str(STD_DIR))
import bilingual_std as B  # noqa: E402

CJK = re.compile(r"[\u2e80-\u9fff\u3000-\u303f\uff00-\uffef]")     # 汉字和全角标点：英文字幕里不该有
WORD = re.compile(r"\w")                                            # 计时只数字和字母（标点、空格不算：build_timeline 会去掉行尾的，）
LATIN = re.compile(r"[A-Za-z][A-Za-z0-9.+\-]*[A-Za-z0-9+]|[A-Za-z]")
NUM = re.compile(r"\d+(?:\.\d+)?")
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def norm(s):
    return "".join(WORD.findall(s))


def split(zh, en, cuts=None):
    """one line -> [(zh_i, en_i, zh width)] by the project standard (manual cuts when given)"""
    cuts = [tuple(c) for c in cuts] if cuts else None
    return B.split_pair_aligned(str(zh).strip(), str(en or "").strip(), cuts=cuts)


def number_alts(zh):
    """English spellings that may stand for a number in the Chinese line: 10 月 -> October, 116 亿 -> 11.6 billion, 3 万 -> 30K"""
    alt = {}
    for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(亿|万)", zh):
        v = float(num) / 10 if unit == "亿" else float(num) * 10
        alt.setdefault(num, []).append(f"{v:g}")
    for num in re.findall(r"(?<![\d.])(\d{1,2})\s*月", zh):
        if 1 <= int(num) <= 12:
            alt.setdefault(num, []).append(MONTHS[int(num) - 1][:3])
    return alt


def check_pair(where, zh, en, cuts=None):
    """(errs, warns) for one subtitle line and its English"""
    errs, warns = [], []
    zh, en = str(zh or "").strip(), str(en or "").strip()
    if not zh:
        return errs, warns
    if not en:
        return [f"{where}「{zh[:16]}」没有英文字幕（en，整句意译）"], warns
    bad = "".join(dict.fromkeys(CJK.findall(en)))
    if bad:
        errs.append(f"{where} 的英文里有中文字符或全角标点「{bad}」：英文字幕只写英文和半角标点")
    low = en.lower()
    miss = [t for t in dict.fromkeys(LATIN.findall(zh)) if t.lower() not in low]
    if miss:
        errs.append(f"{where} 的英文名在英文字幕里没有原样出现：{'、'.join(miss)}（专有名词保留原名）")
    alt = number_alts(zh)
    nmiss = [n for n in dict.fromkeys(NUM.findall(zh)) if n not in en and not any(a.lower() in low for a in alt.get(n, []))]
    if nmiss:
        warns.append(f"{where} 的数字在英文里没找到：{'、'.join(nmiss)}（换算过的写法也行，确认意思一致）")
    try:
        chunks = split(zh, en, cuts)
    except ValueError:
        return errs + [f"{where} 的 cuts 锚点在中文 / 英文里按顺序找不到：{cuts}"], warns
    for k, (z, e, w) in enumerate(chunks, 1):
        tag = f"{where}（第 {k}/{len(chunks)} 条）"
        if not z or not e:
            errs.append(f"{tag} 拆出了空的中文或英文：写 cuts 指定断点")
        elif w > B.ZH_MAX or len(e) > B.EN_SOFT:
            errs.append(f"{tag} 一行放不下（中文 {w:.1f} 字 / 英文 {len(e)} 字符，上限约 28 / 90）：写 cuts 指定断点，或把句子写短")
        elif len(e) > B.EN_MAX:
            warns.append(f"{tag} 英文 {len(e)} 字符，略超 90")
    return errs, warns


def char_times(seg):
    """[(start, end)] of every counted character (letters, digits, CJK) of a timeline segment, from its aligned lines"""
    out = []
    for ln in seg["lines"]:
        n = len(WORD.findall(ln["text"]))
        d = (ln["end"] - ln["start"]) / (n or 1)
        out += [(ln["start"] + d * i, ln["start"] + d * (i + 1)) for i in range(n)]
    return out


def chunk_times(seg, chunks):
    """(start, end) of each chunk: its first and last character's spoken moments (proportional over the segment as a fallback)"""
    ct = char_times(seg)
    counts = [len(WORD.findall(z)) for z, _, _ in chunks]
    if len(ct) != sum(counts) or not ct:
        return B.chunk_times(seg["start"], seg["end"], chunks), False
    out, i = [], 0
    for c in counts:
        a = ct[min(i, len(ct) - 1)][0]
        b = ct[max(i + c - 1, 0)][1] if c else a
        out.append((a, b))
        i += c
    return out, True


def seg_subs(seg, en, cuts=None):
    """subtitle cues of one timeline segment ({text, start, end, lines}) -> ([{zh, en, s, e}], aligned)"""
    chunks = split(seg["text"], en, cuts)
    times, aligned = chunk_times(seg, chunks)
    return [{"zh": z, "en": e, "s": round(s, 3), "e": round(t, 3)} for (z, e, _), (s, t) in zip(chunks, times)], aligned


def set_windows(subs):
    """display window [a, b) of every cue (sorted by time, whole video): 0.1 s before to 0.45 s after, no overlap"""
    for x, (a, b) in zip(subs, B.display_windows([(x["s"], x["e"]) for x in subs])):
        x["a"], x["b"] = round(max(0.0, a), 3), round(b, 3)
    return subs
