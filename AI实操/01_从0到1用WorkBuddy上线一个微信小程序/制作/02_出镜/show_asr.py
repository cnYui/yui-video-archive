# -*- coding: utf-8 -*-
"""看识别结果：python show_asr.py <编号> [-w]（-w 逐词带时间）[--from 秒 --to 秒]"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    a = sys.argv[1:]
    i = a[0]
    words = "-w" in a
    t0 = float(a[a.index("--from") + 1]) if "--from" in a else 0
    t1 = float(a[a.index("--to") + 1]) if "--to" in a else 1e9
    d = json.loads((HERE / "asr" / f"{i}.json").read_text(encoding="utf-8"))
    print(f"# {i}  {d['duration']:.1f}s")
    for s in d["segments"]:
        if s["end"] < t0 or s["start"] > t1:
            continue
        print(f"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text'].strip()}")
        if words:
            print("     " + " ".join(f"{w['w'].strip()}@{w['s']:.2f}" + ("?" if w["p"] < 0.5 else "") for w in s["words"]))


if __name__ == "__main__":
    main()
