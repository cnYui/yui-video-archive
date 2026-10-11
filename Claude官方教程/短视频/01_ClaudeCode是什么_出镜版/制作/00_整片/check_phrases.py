# -*- coding: utf-8 -*-
r"""查 scenes_ep.js 里的 S('Txx') / E('Txx') / P('Txx', '词')：行号存在、词真在那一行的字幕里（P() 找不到词会让整条渲染抛错）。
  python check_phrases.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "台本"))
import talk_lines as TLN  # noqa: E402

zh = {l[0]: l[4] for l in TLN.LINES}
src = "\n".join(l for l in (HERE / "scenes_ep.js").read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("//"))
bad = 0

for m in re.finditer(r"""\b([SE])\('(T\d+)'\)""", src):
    if m.group(2) not in zh:
        print("没有这一行：", m.group(0)); bad += 1
n_lit = 0
for m in re.finditer(r"""\bP\('(T\d+)',\s*'([^']*)'""", src):
    n_lit += 1
    lid, ph = m.group(1), m.group(2)
    if lid not in zh:
        print("没有这一行：", m.group(0)); bad += 1
    elif ph not in zh[lid]:
        print(f"词不在字幕里：P('{lid}', '{ph}')   字幕 = {zh[lid]}"); bad += 1

# 非字面量的 P(...)：数组里的词，手工列出
dyn = {
    "T24": ["找代码", "改代码", "跑命令", "搜索整个项目", "创建文件", "删除文件"],
    "T47": ["每天定时定点", "去搜这些新闻", "把它整理好", "创建一个新的文档"],
    "T74": ["大脑", "双手", "记忆", "钥匙"],
    "T77": ["听懂", "看懂", "决定"],
    "T109": ["大脑", "双手", "记忆", "权限钥匙"],
    "T113": ["幻觉", "概率模型", "bug"],
}
for lid, phs in dyn.items():
    for ph in phs:
        if ph not in zh[lid]:
            print(f"（数组里的）词不在字幕里：{lid} '{ph}'"); bad += 1
print(f"检查了 {n_lit} 个字面量 P() + {sum(len(v) for v in dyn.values())} 个数组词：{'全部在字幕里' if not bad else str(bad) + ' 处有问题'}")
sys.exit(1 if bad else 0)
