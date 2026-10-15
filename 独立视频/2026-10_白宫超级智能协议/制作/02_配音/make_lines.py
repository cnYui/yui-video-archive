# -*- coding: utf-8 -*-
"""台本 → 配音用的句子表 tts/lines.json，和要粘进 Fish 网页版的整期文本 tts/paste.txt（一句一行）。

  python make_lines.py

Fish 网页版：声音「赛马娘（曼波欧耶版）」，整期一次生成（一次出两个版本，v1 / v2）。
录制稿里某句带 "batch": "I" 的是另一次生成（例：片尾彩蛋 K8 的两句同传），不放进 paste.txt，单独写 paste_I.txt。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
sc = json.loads((EP / "台本" / "录制稿_v2.json").read_text(encoding="utf-8"))
lines = [{"id": l["id"], "zh": l["zh"], "say": l["say"], **({"batch": l["batch"]} if "batch" in l else {})} for l in sc["lines"]]
(HERE / "tts").mkdir(exist_ok=True)
(HERE / "tts" / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
main = [l for l in lines if "batch" not in l]
(HERE / "tts" / "paste.txt").write_text("\n".join(l["say"] for l in main) + "\n", encoding="utf-8")
n = sum(len(l["say"]) for l in main)
print(f"{len(lines)} 句；主批 {len(main)} 句、{n} 字，paste.txt 已写。")
for b in sorted({l["batch"] for l in lines if "batch" in l}):
    ls = [l for l in lines if l.get("batch") == b]
    (HERE / "tts" / f"paste_{b}.txt").write_text("\n".join(l["say"] for l in ls) + "\n", encoding="utf-8")
    print(f"批 {b}：{len(ls)} 句，paste_{b}.txt 已写。")
