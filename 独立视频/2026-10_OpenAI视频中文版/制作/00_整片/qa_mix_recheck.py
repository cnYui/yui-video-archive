# -*- coding: utf-8 -*-
"""不重新识别，直接用 qa_mix_log.txt 里已有的识别结果重算相似度：阿拉伯数字换回汉字、刀子 / DOTS → dot、全部小写，再和配音文本比。

  python qa_mix_recheck.py
"""
import difflib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = "零一二三四五六七八九"


def cn(k):
    if k < 10:
        return D[k]
    if k < 20:
        return "十" + (D[k % 10] if k % 10 else "")
    if k < 100:
        return D[k // 10] + "十" + (D[k % 10] if k % 10 else "")
    if k < 1000:
        h, r = divmod(k, 100)
        return D[h] + "百" + ("" if r == 0 else ("零" + D[r] if r < 10 else cn(r)))
    t, r = divmod(k, 1000)
    return D[t] + "千" + ("" if r == 0 else ("零" + cn(r) if r < 100 else cn(r)))


def n(s):
    s = re.sub(r"\d+", lambda m: cn(int(m.group())) if int(m.group()) < 10000 else m.group(), s)
    s = s.replace("刀子", "dot").replace("刀", "dot")
    return re.sub(r"[^\w]|_", "", s.lower())


def main():
    T = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
    say = {c["id"]: c["say"] for c in T["cues"]}
    rows = []
    for ln in (HERE / "qa_mix_log.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"(N\d{3})\s+([\d.]+)\s+([\d.]+)\s+(.*?)(\s+<<<)?$", ln)
        if m:
            cid, t, old, hyp = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
            rows.append((cid, t, old, difflib.SequenceMatcher(None, n(say[cid]), n(hyp)).ratio(), hyp))
    low = [r for r in rows if r[3] < 0.85]
    print(f"已识别 {len(rows)} 句；归一化后低于 0.85 的 {len(low)} 句：")
    for cid, t, old, new, hyp in low:
        print(f"  {cid} @{t:.1f}s 原分 {old:.2f} → {new:.2f}  稿：{say[cid][:40]}\n        识别：{hyp[:60]}")
    if rows:
        print(f"平均分 {sum(r[3] for r in rows) / len(rows):.3f}，最低 {min(r[3] for r in rows):.2f}")


if __name__ == "__main__":
    main()
