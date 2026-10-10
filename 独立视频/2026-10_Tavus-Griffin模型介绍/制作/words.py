# -*- coding: utf-8 -*-
r"""查素材视频里每个词的时间（词级转写：素材/转写/<视频名>.words.json）。

  python words.py gr 27 37            打印 27–37 s 之间的词，带起止时间
  python words.py el 90 120 -s        按句号 / 停顿(>0.35 s) 合并成一行一行
短名：gr = Griffin 发布视频，el = Elevare，me = Memories。
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = {"gr": "tavus_2105704169009246248", "el": "tavus_2104998304279048334", "me": "tavus_2100277005841469469"}


def main():
    key, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    words = json.loads((HERE.parent / "素材" / "转写" / f"{NAMES[key]}.words.json").read_text(encoding="utf-8"))
    ws = [w for w in words if w["e"] >= a and w["s"] <= b]
    if "-s" in sys.argv:
        line, start, last = [], None, None
        for w in ws:
            if line and (w["s"] - last > 0.35 or line[-1].rstrip().endswith((".", "?", "!"))):
                print(f"[{start:7.2f}–{last:7.2f}] {''.join(line).strip()}")
                line, start = [], None
            if start is None:
                start = w["s"]
            line.append(w["w"])
            last = w["e"]
        if line:
            print(f"[{start:7.2f}–{last:7.2f}] {''.join(line).strip()}")
        return
    for w in ws:
        print(f"{w['s']:7.2f} {w['e']:7.2f}  {w['w'].strip():<14s} p={w['p']}")


if __name__ == "__main__":
    main()
