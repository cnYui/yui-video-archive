# -*- coding: utf-8 -*-
"""台本 → 配音用的句子表 tts/lines.json，和要粘进 Fish 网页版的整期文本 tts/paste.txt（一句一行）。

  python make_lines.py

Fish 网页版：声音「赛马娘（曼波欧耶版）」，模型 S2 Pro，整期一次生成（一次出两个版本，v1 / v2）。
say 里去掉「」“”引号（念出来没有意义），把“——”换成逗号（停一下）。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]


def clean(s):
    s = re.sub(r"[「」“”‘’]", "", s)
    return s.replace("——", "，").replace("，，", "，")


def main():
    sc = json.loads((EP / "台本" / "录制稿_v1.json").read_text(encoding="utf-8"))["lines"]
    lines = [{"id": l["id"], "zh": l["zh"], "say": clean(l["say"])} for l in sc]
    (HERE / "tts").mkdir(exist_ok=True)
    (HERE / "tts" / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "tts" / "paste.txt").write_text("\n".join(l["say"] for l in lines) + "\n", encoding="utf-8")
    n = sum(len(l["say"]) for l in lines)
    print(f"{len(lines)} 句，{n} 字（{len(''.join(l['say'] for l in lines).encode('utf-8'))} 字节；Fish 页面按字节算，上限 15000），paste.txt 已写。")


if __name__ == "__main__":
    main()
