# -*- coding: utf-8 -*-
r"""把十期的配音文本导成一份 markdown：每期按成片里出现的顺序编号；字幕写法和实际念的写法不同的句子（Claude 点 md、斜杠 compact……）单列在每期后面。

  python export_voice_text.py            → Claude官方教程\配音文本_第1-10期.md
数据取自各期 台本\录制稿.json（渲成片用的就是它：zh = 字幕 / 给人读的写法，say = 送去配音的写法）。
"""
import json
from pathlib import Path

ROOT = Path(r"D:\大疆\Claude官方教程")
OUT = ROOT / "配音文本_第1-10期.md"


def main():
    parts = ["# 《Claude官方教程》系列① 十期配音文本", "",
             "每期按成片里的顺序编号。正文是字幕写法（给人读的写法）；配音实际念的写法和它不一样的地方，列在每期后面“念法不同”里（英文名、命令、符号按读音拼出来，方便 TTS 念对）。声线：Fish Audio「温柔男生」，第三人称讲解。", ""]
    total = 0
    for d in sorted((ROOT / "短视频").glob("[0-9][0-9]_*")):
        j = json.loads((d / "台本" / "录制稿.json").read_text(encoding="utf-8"))
        lines = j["lines"]
        n = int(d.name[:2])
        title = j["title"].replace("Claude官方教程 ", "")
        chars = sum(len(l["zh"]) for l in lines)
        total += chars
        parts += [f"## {title}", "", f"（{len(lines)} 句，{chars} 字）", ""]
        for k, l in enumerate(lines, 1):
            parts.append(f"{k}. {l['zh']}")
        diff = [(k, l) for k, l in enumerate(lines, 1) if l.get("say") and l["say"] != l["zh"]]
        if diff:
            parts += ["", "念法不同："]
            for k, l in diff:
                parts.append(f"- 第 {k} 句：{l['say']}")
        parts.append("")
    parts.append(f"合计 {total} 字。")
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(OUT, total)


if __name__ == "__main__":
    main()
