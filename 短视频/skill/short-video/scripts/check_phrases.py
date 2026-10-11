# -*- coding: utf-8 -*-
r"""查叠加层脚本（scenes*.js）里 S('id') / E('id') / P('id', '词') 用到的字幕行和词是不是真在字幕里。

  python check_phrases.py <本条目录> [--dyn dyn.json]

为什么：`P(id, 词)` 在字幕里找不到词会抛错，整条渲染都挂；`S` / `E` 的 id 不存在也一样。写完 scenes_ep.js 先跑一遍，比等渲染报错省十分钟。
读 <本条>\台本\录制稿.json 的 lines（id → zh），扫 <本条>\制作\00_整片\scenes*.js（跳过 // 注释行）：
  · S('T20') / E('T20')：id 要存在；
  · P('T20', '顾问')：词要在这一行的 zh 里；
  · P('T20', ROWS[i][2]) 这种词不是字面量的查不了，列出来；把这些词写进 dyn.json（{"T24": ["找代码", "改代码"]}）再 --dyn 一起查。
有问题退出码 1。
"""
import json
import re
import sys
from pathlib import Path


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    ep = Path(args[0])
    sc = json.loads((ep / "台本" / "录制稿.json").read_text(encoding="utf-8"))
    zh = {l["id"]: l["zh"] for l in sc["lines"]}
    src = ""
    for f in sorted((ep / "制作" / "00_整片").glob("scenes*.js")):
        src += "\n".join(l for l in f.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("//")) + "\n"
    bad = 0
    for m in re.finditer(r"""\b([SE])\('([^']+)'\)""", src):
        if m.group(2) not in zh:
            print("没有这一行：", m.group(0))
            bad += 1
    n_lit = n_dyn = 0
    for m in re.finditer(r"""\bP\('([^']+)',\s*('([^']*)'|[^)\s][^)]*)""", src):
        lid, tail, lit = m.group(1), m.group(2), m.group(3)
        if lit is None:
            n_dyn += 1
            print(f"（查不了）P('{lid}', {tail[:40]}…) 的词不是字面量，写进 --dyn 再查")
            continue
        n_lit += 1
        if lid not in zh:
            print("没有这一行：", m.group(0))
            bad += 1
        elif lit not in zh[lid]:
            print(f"词不在字幕里：P('{lid}', '{lit}')   字幕 = {zh[lid]}")
            bad += 1
    n_arr = 0
    if "--dyn" in args:
        for lid, phs in json.loads(Path(args[args.index("--dyn") + 1]).read_text(encoding="utf-8")).items():
            for ph in phs:
                n_arr += 1
                if lid not in zh or ph not in zh[lid]:
                    print(f"（--dyn）词不在字幕里：{lid} '{ph}'")
                    bad += 1
    print(f"检查了 {n_lit} 个字面量 P() + {n_arr} 个 --dyn 词（{n_dyn} 个非字面量没查）：{'全部在字幕里' if not bad else str(bad) + ' 处有问题'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
