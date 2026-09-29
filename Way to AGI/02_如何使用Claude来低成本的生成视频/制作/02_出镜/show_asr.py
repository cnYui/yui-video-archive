# -*- coding: utf-8 -*-
"""打印识别结果：每段一行（起止秒 + 文字）；加 -w 打印逐词时间。"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
words = "-w" in sys.argv
ids = [a for a in sys.argv[1:] if a != "-w"]
for i in ids:
    d = json.loads((HERE / "asr" / f"{i}.json").read_text(encoding="utf-8"))
    print(f"=== {i} ({d['duration']:.1f}s)")
    for s in d["segments"]:
        if words:
            print("  " + " ".join(f"{w['w'].strip()}[{w['s']:.2f}-{w['e']:.2f}]" for w in s["words"]))
        else:
            print(f"  [{s['start']:6.2f}-{s['end']:6.2f}] {s['text'].strip()}")
