# -*- coding: utf-8 -*-
r"""10 期的配音合成一份 Fish 故事工作室整稿（一个空白项目、分段键入、一次生成、一次导出“按段落拆分”）。

  python build_fish_doc.py                 写 fish_all_say_lines.txt（一行一句，各期顺序拼起来），打印每期句数 / 字数、整稿 SHA-256、分段键入计划（每段 ≤ 24 句）
  python build_fish_doc.py --chunk K       打印第 K 段要键入的文字（第 0 段不带开头换行，后几段以换行开头）
  python build_fish_doc.py --only 1 2      只含这几期（补句 / 先试几期时用）

键入后用 JS 读 div.content 拼起来（换行连接）算 SHA-256，和这里的哈希一致才点“生成”。
"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series_data import EPISODES  # noqa: E402

CHUNK = 24


def all_lines(only=None):
    rows = []
    for n in sorted(EPISODES):
        if only and n not in only:
            continue
        for l in EPISODES[n]["lines"]:
            rows.append((n, l["id"], l["say"]))
    return rows


def main():
    only = None
    if "--only" in sys.argv:
        i = sys.argv.index("--only") + 1
        only = []
        while i < len(sys.argv) and sys.argv[i].isdigit():
            only.append(int(sys.argv[i]))
            i += 1
    rows = all_lines(only)
    says = [r[2] for r in rows]
    text = "\n".join(says)
    out = HERE / ("fish_all_say_lines.txt" if not only else f"fish_say_lines_{'_'.join(map(str, only))}.txt")
    out.write_text(text + "\n", encoding="utf-8")
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    chunks = [says[i:i + CHUNK] for i in range(0, len(says), CHUNK)]
    if "--chunk" in sys.argv:
        k = int(sys.argv[sys.argv.index("--chunk") + 1])
        print(("" if k == 0 else "\n") + "\n".join(chunks[k]), end="")
        return
    for n in sorted({r[0] for r in rows}):
        s = [r[2] for r in rows if r[0] == n]
        print(f"第 {n} 期：{len(s)} 句，{sum(len(x) for x in s)} 字符")
    print(f"合计 {len(says)} 句，{len(text)} 字符；整稿 SHA-256（换行连接、无结尾换行）= {h}")
    print(f"分 {len(chunks)} 段键入：" + "，".join(f"第{i}段 {len(c)} 句" for i, c in enumerate(chunks)))
    print("第 k 段文字：python build_fish_doc.py --chunk k")


if __name__ == "__main__":
    main()
