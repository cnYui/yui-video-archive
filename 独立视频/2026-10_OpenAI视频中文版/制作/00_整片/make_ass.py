# -*- coding: utf-8 -*-
"""timeline.json 的 cues → bilingual.ass（1920×1080，中文大字在上、英文小字在下，成对出现）。

  python make_ass.py

每条 cue：zh（中文，配音念的就是这句）、en（原话）、s/e（中文同传念出来的起止）、who（讲话人，dot 的话带橙色“dot：”）。
- 中英文都按句子拆开（句数对得上才拆），一屏最多两行中文 + 两行英文；每一屏的出现时刻按这一屏中文字数占整句的比例，分配在 s…e 里。
- 显示区间 = s − 0.08 … e + 0.15，让字幕和听到的中文同步；相邻两条之间留 0.04 s，不叠。
- 片头另有一条来源角标（左上角，前 6 秒）。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = "Noto Sans SC"
ZH_SIZE, EN_SIZE = 48, 30
ZH_MAX, EN_MAX = 30, 100           # 每行最多多少个中文字 / 英文字符
BRIGHT_T = 115                     # 字幕区平均亮度超过它的地方（笔记本屏幕、录屏）改用半透明黑底
CREDIT = "画面：OpenAI 官方 YouTube《The dots demo, take two》｜原声压低，中文同传"
NL = "\\N"                          # ASS 里的硬换行


def load_brightness():
    f = HERE / "brightness.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else []


def bright_in(samples, a, b):
    ys = [y for t, y in samples if a - 0.25 <= t <= b + 0.25]
    return sum(ys) / len(ys) if ys else 0.0


def ts(t):
    t = max(0.0, t)
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h}:{m:02d}:{t % 60:05.2f}"


def esc(s):
    return s.replace("{", "(").replace("}", ")")


def merge_short(parts, limit, sep):
    """极短的句子（“Hi.”“Sorry.”“嗨。”）不单独占一屏：开头的并进后一句，其余并进前一句。"""
    parts = list(parts)
    if len(parts) > 1 and len(parts[0]) <= limit:
        parts = [parts[0] + sep + parts[1]] + parts[2:]
    res = []
    for p in parts:
        if res and len(p) <= limit:
            res[-1] = res[-1] + sep + p
        else:
            res.append(p)
    return res


def split_zh(s):
    return merge_short([p.strip() for p in re.findall(r"[^。！？]+[。！？]?", s) if p.strip()], 4, "")


def split_en(s):
    return merge_short([p.strip() for p in re.split(r"(?<=[.?!])\s+(?=[A-Z\"'(])", s.strip()) if p.strip()], 7, " ")


def wrap_zh(s):
    """一行放得下就不折；两行以内尽量折在中间的逗号上；更长就按最大行宽贪心填；不让标点单独成行。"""
    s = s.strip()
    if len(s) <= ZH_MAX:
        return [s]
    clauses = re.findall(r"[^，、：；]+[，、：；]?", s)
    if len(s) <= 2 * ZH_MAX:
        best, acc = None, 0
        for c in clauses[:-1]:
            acc += len(c)
            if acc <= ZH_MAX and len(s) - acc <= ZH_MAX and (best is None or abs(acc - (len(s) - acc)) < abs(best - (len(s) - best))):
                best = acc
        if best is not None:
            return [s[:best], s[best:]]
        half = (len(s) + 1) // 2
        return [s[:half], s[half:]]
    lines, cur = [], ""
    for c in clauses:
        if len(cur) + len(c) <= ZH_MAX:
            cur += c
        else:
            if cur:
                lines.append(cur)
            if len(c) > ZH_MAX:
                k = -(-len(c) // ZH_MAX)
                size = -(-len(c) // k)
                pieces = [c[i:i + size] for i in range(0, len(c), size)]
                lines.extend(pieces[:-1])
                cur = pieces[-1]
            else:
                cur = c
    if cur:
        lines.append(cur)
    return lines


def wrap_en(s):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= EN_MAX:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) == 2 and len(lines[1]) < 0.35 * len(lines[0]):          # 两行太不均匀：从中间折
        half = len(s) // 2
        k = s.rfind(" ", 0, half + 8)
        if k > 0:
            lines = [s[:k], s[k + 1:]]
    return lines


def group_fine(fine, fracs, sep):
    """把句子多的一边（fine）按累计字数占比并成 len(fracs)+1 组：每个分界取最接近 fracs 的句间位置。"""
    lens = [len(x) for x in fine]
    total, acc, cum = sum(lens), 0, []
    for n in lens[:-1]:
        acc += n
        cum.append(acc / total)
    cuts, last = [], -1
    for j, f in enumerate(fracs):
        lo, hi = last + 1, len(cum) - 1 - (len(fracs) - j - 1)
        idx = min(range(lo, hi + 1), key=lambda t: abs(cum[t] - f))
        cuts.append(idx)
        last = idx
    groups, start = [], 0
    for c in cuts:
        groups.append(sep.join(fine[start:c + 1]))
        start = c + 1
    groups.append(sep.join(fine[start:]))
    return groups


def chunks_of(q):
    """一条 cue → ([(中文, 英文, 占的字数)], 是否原本句数就对得上)。句数不同就把句子多的一边按字数占比合并，保证每一屏中英对得上。"""
    zs, es = split_zh(q["zh"]), split_en(q["en"])
    if len(zs) == 1 or len(es) == 1:
        return [(q["zh"], q["en"], len(q["zh"]))], len(zs) == len(es)
    k = min(len(zs), len(es))
    if len(zs) == len(es):
        pairs = list(zip(zs, es))
    elif len(zs) == k:
        tot, acc, fr = sum(len(z) for z in zs), 0, []
        for z in zs[:-1]:
            acc += len(z)
            fr.append(acc / tot)
        pairs = list(zip(zs, group_fine(es, fr, " ")))
    else:
        tot, acc, fr = sum(len(e) for e in es), 0, []
        for e in es[:-1]:
            acc += len(e)
            fr.append(acc / tot)
        pairs = list(zip(group_fine(zs, fr, ""), es))
    return [(z, e, len(z)) for z, e in pairs], len(zs) == len(es)


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    cues = sorted(T["cues"], key=lambda q: q["s"])
    events, mismatched, n_chunks, n_boxed = [], [], 0, 0
    samples = load_brightness()
    for i, q in enumerate(cues):
        ch, same = chunks_of(q)
        if not same:
            mismatched.append(q["id"])
        t0, t1 = q["s"] - 0.08, max(q["e"] + 0.15, min(q["src"][1] + 0.12, q["e"] + 3.5))
        if i + 1 < len(cues):
            t1 = min(t1, cues[i + 1]["s"] - 0.08 - 0.04)
        total = sum(c[2] for c in ch)
        cum, starts = 0, []
        for k, c in enumerate(ch):
            starts.append(t0 if k == 0 else q["s"] + (q["e"] - q["s"]) * cum / total)
            cum += c[2]
        starts.append(t1)
        for k, (z, e, _) in enumerate(ch):
            a, b = starts[k], max(starts[k + 1], starts[k] + 0.7)
            zh = wrap_zh(esc(z))
            if q.get("who"):
                zh[0] = "{\\c&H4AA8FF&}" + esc(q["who"]) + "：{\\c&HFFFFFF&}" + zh[0]
            en = wrap_en(esc(e))
            boxed = bright_in(samples, a, b) > BRIGHT_T
            n_boxed += boxed
            txt = NL.join(zh) + NL + ("{\\rENB}" if boxed else "{\\rEN}") + NL.join(en)
            events.append(f"Dialogue: 0,{ts(a)},{ts(b)},{'ZHB' if boxed else 'ZH'},,0,0,0,,{txt}")
            n_chunks += 1
    events.append(f"Dialogue: 1,{ts(0.3)},{ts(6.3)},TAG,,0,0,0,,{{\\fad(300,500)}}{CREDIT}")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ZH,{FONT},{ZH_SIZE},&H00FFFFFF,&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,3.2,1.2,2,120,120,60,1
Style: EN,{FONT},{EN_SIZE},&H00E6E6E6,&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2.4,1,2,120,120,60,1
Style: ZHB,{FONT},{ZH_SIZE},&H00FFFFFF,&H000000FF,&H8C000000,&H00000000,0,0,0,0,100,100,0,0,3,9,0,2,120,120,60,1
Style: ENB,{FONT},{EN_SIZE},&H00E6E6E6,&H000000FF,&H8C000000,&H00000000,0,0,0,0,100,100,0,0,3,7,0,2,120,120,60,1
Style: TAG,{FONT},28,&H00FFFFFF,&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,2,0.8,7,48,48,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    (HERE / "bilingual.ass").write_text(head + "\n".join(events) + "\n", encoding="utf-8")
    print(f"bilingual.ass：{len(cues)} 条 cue 拆成 {n_chunks} 屏中英字幕（其中 {n_boxed} 屏在亮背景上加了半透明黑底）+ 1 条来源角标；中英句数对不上、整条一屏的：{' '.join(mismatched) or '无'}")


if __name__ == "__main__":
    main()
