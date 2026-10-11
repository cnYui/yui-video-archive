# -*- coding: utf-8 -*-
"""查某段时间里每个词的时间（定剪辑入出点和同传锚点用）。

  python words.py 145 165            → 145–165 s 之间的句子，每句带起止时间
  python words.py 145 165 -w         → 再加每个词的时间（词@起始秒）
  python words.py 145 165 --fine     → 用 part_*_fine.json（对这一段 beam 5 精转的）
读 素材/转写/keynote.json（merge_transcripts.py 合并的）。
"""
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "素材" / "转写"


def main():
    a, b = float(sys.argv[1]), float(sys.argv[2])
    show_words = "-w" in sys.argv
    if "--fine" in sys.argv:
        segs = []
        for p in sorted(D.glob("part_*_fine.json")):
            segs += json.loads(p.read_text(encoding="utf-8"))["segments"]
    else:
        segs = json.loads((D / "keynote.json").read_text(encoding="utf-8"))["segments"]
    for s in segs:
        if s["end"] < a or s["start"] > b:
            continue
        print(f"[{s['start']:8.2f}–{s['end']:8.2f}] {s['text']}")
        if show_words:
            print("    " + " ".join(f"{w['w'].strip()}@{w['s']:.2f}" for w in s["words"] if a - 0.5 <= w["s"] <= b + 0.5))


if __name__ == "__main__":
    main()
