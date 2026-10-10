# -*- coding: utf-8 -*-
"""台本（台本/V?_*.json 里所有视频）→ 配音用的句子表 tts/lines.json，和要粘进 Fish 网页版的文本 tts/paste_<批>.txt（一句一行）。

  python make_lines.py

Fish 网页版：声音「赛马娘（曼波欧耶版）」，一批一次生成（一次出两个版本，v1 / v2）。
哪个视频进哪一批由台本里的 "batch" 定（默认 A）：同一批里的句子音色、语气最统一；以后某条要改稿，只重生成它那一批。
句子的先后 = 台本文件名顺序 × 句子在台本里的顺序；tts_build.py 按这个顺序把各批拼成一条口播。
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
lines = []
for f in sorted((EP / "台本").glob("V?_*.json")):
    sc = json.loads(f.read_text(encoding="utf-8"))
    for l in sc["lines"]:
        lines.append({"id": l["id"], "zh": l["zh"], "say": l["say"], "batch": sc.get("batch", "A")})
ids = [l["id"] for l in lines]
assert len(ids) == len(set(ids)), "句子号有重复"
(HERE / "tts").mkdir(exist_ok=True)
(HERE / "tts" / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"共 {len(lines)} 句，{sum(len(l['say']) for l in lines)} 字")
for b in sorted({l["batch"] for l in lines}):
    ls = [l for l in lines if l["batch"] == b]
    (HERE / "tts" / f"paste_{b}.txt").write_text("\n".join(l["say"] for l in ls) + "\n", encoding="utf-8")
    n = sum(len(l["say"]) for l in ls)
    print(f"批 {b}：{len(ls)} 句、{n} 字（约 {n / 6.3:.0f} s），paste_{b}.txt 已写")
