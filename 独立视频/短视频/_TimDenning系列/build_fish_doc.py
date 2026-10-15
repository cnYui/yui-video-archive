# -*- coding: utf-8 -*-
"""6 期的配音合成一份 Fish 故事工作室整稿（一个空白项目、一次键入、一次生成、一次导出“按段落拆分”）。

  python build_fish_doc.py            写 fish_all_say_lines.txt（一行一句，6 期顺序拼起来），打印每期句数 / 字数、整稿 SHA-256、分段键入计划（每段 ≤ 24 句）
  python build_fish_doc.py --chunk K  打印第 K 段要键入的文字（第 0 段不带开头换行，后几段以换行开头）

键入后用 JS 读 div.content 拼起来（换行连接）算 SHA-256，和这里的哈希一致才点“生成”。
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import series_data as D  # noqa: E402

CHUNK = 24


def all_lines():
    rows = []
    for ep in D.EPISODES:
        for sc in ep["scenes"]:
            for ln in sc["lines"]:
                rows.append((ep["num"], ln["id"], ln["say"]))
    return rows


def main():
    rows = all_lines()
    says = [r[2] for r in rows]
    text = "\n".join(says)
    (HERE / "fish_all_say_lines.txt").write_text(text + "\n", encoding="utf-8")
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    chunks = [says[i:i + CHUNK] for i in range(0, len(says), CHUNK)]
    if "--chunk" in sys.argv:
        k = int(sys.argv[sys.argv.index("--chunk") + 1])
        print(("" if k == 0 else "\n") + "\n".join(chunks[k]), end="")
        return
    for ep in D.EPISODES:
        s = [r[2] for r in rows if r[0] == ep["num"]]
        print(f"第 {ep['num']} 期：{len(s)} 句，{sum(len(x) for x in s)} 字符")
    print(f"合计 {len(says)} 句，{len(text)} 字符；整稿 SHA-256（换行连接、无结尾换行）= {h}")
    print(f"分 {len(chunks)} 段键入：" + "，".join(f"第{i}段 {len(c)} 句" for i, c in enumerate(chunks)))
    print("第 k 段文字：python build_fish_doc.py --chunk k")


if __name__ == "__main__":
    main()
