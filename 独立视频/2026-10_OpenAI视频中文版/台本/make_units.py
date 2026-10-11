# -*- coding: utf-8 -*-
"""en_asr.json（逐词时间）→ units.json + units.txt：按停顿切成可翻译的小句，每句 U001… 带起止时间，写译文时按编号引用。

  python make_units.py

切法：相邻两词间隔 ≥ GAP_BREAK 就断；句末标点后且这一句已有 ≥ MIN_LEN 秒也断；一句超过 MAX_LEN 秒，在其中最长的词间停顿处再断一次。
英文原文里的口癖（um / uh）保留在 units.json，写译文时直接略过。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
GAP_BREAK, MIN_LEN, MAX_LEN = 0.55, 2.0, 9.0


def main():
    d = json.loads((HERE / "en_asr.json").read_text(encoding="utf-8"))
    words = [w for s in d["segments"] for w in s["words"]]
    units, cur = [], []

    def flush():
        nonlocal cur
        if cur:
            units.append(cur)
            cur = []

    for i, w in enumerate(words):
        cur.append(w)
        gap = words[i + 1]["s"] - w["e"] if i + 1 < len(words) else 99
        dur = w["e"] - cur[0]["s"]
        if gap >= GAP_BREAK or (re.search(r"[.?!][\"')\]]*$", w["w"].strip()) and dur >= MIN_LEN):
            flush()
    flush()
    out = []
    for ws in units:
        stack = [ws]
        while stack:
            u = stack.pop(0)
            if u[-1]["e"] - u[0]["s"] > MAX_LEN and len(u) > 6:
                k = max(range(2, len(u) - 2), key=lambda j: u[j]["s"] - u[j - 1]["e"])
                stack = [u[:k], u[k:]] + stack
            else:
                out.append(u)
    res = []
    for i, u in enumerate(out, 1):
        res.append({"id": f"U{i:03d}", "s": round(u[0]["s"], 2), "e": round(u[-1]["e"], 2), "en": "".join(w["w"] for w in u).strip()})
    (HERE / "units.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "units.txt").write_text("\n".join(f"{r['id']} [{r['s']:6.2f}-{r['e']:6.2f}] {r['en']}" for r in res) + "\n", encoding="utf-8")
    print(f"{len(res)} 个小句；总说话时间 {sum(r['e'] - r['s'] for r in res):.0f} s；最长 {max(r['e'] - r['s'] for r in res):.1f} s")


if __name__ == "__main__":
    main()
