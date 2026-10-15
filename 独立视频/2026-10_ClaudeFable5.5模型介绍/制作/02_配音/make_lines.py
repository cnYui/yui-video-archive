# -*- coding: utf-8 -*-
"""台本 → 配音用的句子表 tts/lines.json，和要粘进 Fish 网页版的整期文本 tts/paste.txt（一句一行）。

  python make_lines.py

Fish 网页版：声音「赛马娘（曼波欧耶版）」，整期一次生成（一次出两个版本，存成 tts/raw/N_v1.mp3、N_v2.mp3）。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
sc = json.loads((EP / "台本" / "录制稿.json").read_text(encoding="utf-8"))
lines = [{"id": l["id"], "zh": l["zh"], "say": l["say"]} for l in sc["lines"]]
(HERE / "tts").mkdir(exist_ok=True)
(HERE / "tts" / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
(HERE / "tts" / "paste.txt").write_text("\n".join(l["say"] for l in lines) + "\n", encoding="utf-8")
n = sum(len(l["say"]) for l in lines)
print(f"{len(lines)} 句、{n} 字（Fish 页面按字节算约 {sum(len(l['say'].encode('utf-8')) for l in lines)} 字节），paste.txt 已写。")
