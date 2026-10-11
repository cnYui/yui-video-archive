# -*- coding: utf-8 -*-
"""把 20 张对比图的数据合并成引擎要的 rules.js（window.RULES / window.IMGS），并把图片拷进 media/img/。

输入：
  ../../台本/rules_meta.json         script_src.py 生成：每条规则的标题、书里的英文章名、页码、“记住”一句、标签、说明栏文字
  ../../台本/marks/marks_*.json      标注子代理量的：每张图的 size、sets（面板 L / R 外框、高亮框 hl）
  ../../台本/录制稿.json              句子（每条规则有哪几句，按“左边 / 右边”自动排讲解步骤）
  ../../台本/steps.json（可选）       手写覆盖：{"13": {"takeAt": "R13g", "steps": [{"at": "R13a", "set": 0, "focus": "both", "hl": []}, …]}}
输出：rules.js、media/img/*.jpg

自动步骤：第一句 both；之后每句看有没有“左边 / 左下角 / 右边”：提到哪边就把焦点切过去并亮出那边的下一个高亮框（同一边连续几句，一句多亮一个）；
没提边的句子沿用上一句的焦点；最后一句（总结）回到 both、高亮全收。
"""
import json
import re
import shutil
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]
SC = EP / "台本"
MAT = Path(r"D:\大疆\独立视频\素材\2026-10_人人都是UI设计师") / "图片"
OUT = HERE / "media" / "img"


def load_marks():
    marks = {}
    for f in sorted((SC / "marks").glob("marks_*.json")):
        marks.update(json.loads(f.read_text(encoding="utf-8")))
    return marks


def auto_steps(ids, zh, sets):
    hlL = [i for i, h in enumerate(sets[0]["hl"]) if h["p"] == "L"]
    hlR = [i for i, h in enumerate(sets[0]["hl"]) if h["p"] == "R"]
    steps, side, nl, nr = [], "both", 0, 0
    for k, (i, z) in enumerate(zip(ids, zh)):
        last = k == len(ids) - 1
        if k == 0:
            steps.append({"at": i, "focus": "both", "hl": []}); continue
        s = "L" if re.search("左边|左下角|左上|左侧", z) else "R" if re.search("右边|右侧", z) else None
        if last and s is None:
            steps.append({"at": i, "focus": "both", "hl": []}); side = "both"; continue
        if s is None:
            s = side if side in ("L", "R") else "both"
        if s == "L":
            nl = nl + 1 if side == "L" else 1
            show = hlL[:nl]
        elif s == "R":
            nr = nr + 1 if side == "R" else 1
            show = hlR[:nr]
        else:
            show = []
        side = s
        steps.append({"at": i, "focus": s, "hl": show})
    return steps


def main():
    meta = json.loads((SC / "rules_meta.json").read_text(encoding="utf-8"))
    marks = load_marks()
    sc = json.loads((SC / "录制稿.json").read_text(encoding="utf-8"))
    lines = {l["id"]: l for l in sc["lines"]}
    steps_over = json.loads((SC / "steps.json").read_text(encoding="utf-8")) if (SC / "steps.json").exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)
    rules, imgs, miss = {}, {}, []
    for n, m in meta.items():
        key = m["img"]
        if key not in marks:
            miss.append(key); continue
        mk = marks[key]
        size = list(Image.open(MAT / key).size)
        assert size == mk["size"], f"{key} 尺寸对不上：标注 {mk['size']}，图片 {size}"
        ids = [l["id"] for l in sc["lines"] if l["id"].startswith(f"R{int(n):02d}")]
        ov = steps_over.get(str(n), {})
        steps = ov.get("steps") or auto_steps(ids, [lines[i]["zh"] for i in ids], mk["sets"])
        for s in steps:
            assert s["at"] in lines, f"规则 {n}：步骤里的句子 {s['at']} 不存在"
            assert not s.get("phrase") or s["phrase"] in lines[s["at"]]["zh"], f"规则 {n}：「{s['phrase']}」不在 {s['at']} 的字幕里：{lines[s['at']]['zh']}"
            si = s.get("set", 0)
            for k in s.get("hl", []):
                assert k < len(mk["sets"][si]["hl"]), f"规则 {n}：set {si} 没有第 {k} 个高亮框"
        sets = [dict(st, **(ov.get("sets", [{}] * 9)[i] if i < len(ov.get("sets", [])) else {})) for i, st in enumerate(mk["sets"])]      # 每套面板可以单独换标签 / 说明（图 13 上层没有 ✕ / ✓）
        for st in sets:                                                                         # roles：{"L": "warn"} 把这一边的高亮框都换成这个颜色（neutral 蓝 / warn 琥珀）
            for h in st["hl"]:
                h["role"] = ov.get("roles", {}).get(h["p"], h["role"])
        rules[int(n)] = dict(m, size=size, sets=sets, steps=steps, takeAt=ov.get("takeAt"))
        shutil.copy2(MAT / key, OUT / key)
        imgs[key] = size
    # 非规则用到的图：文章封面
    cover = "图00_封面.jpg"
    shutil.copy2(MAT / cover, OUT / cover)
    imgs[cover] = list(Image.open(MAT / cover).size)
    (HERE / "rules.js").write_text("window.RULES = " + json.dumps(rules, ensure_ascii=False, separators=(",", ":")) + ";\nwindow.IMGS = " + json.dumps(imgs, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"rules.js：{len(rules)} 条规则，{len(imgs)} 张图" + (f"；缺标注：{miss}" if miss else ""))
    for n in sorted(rules):
        r = rules[n]
        print(f"  {n:2d} {r['title']}  size {r['size']}  sets {len(r['sets'])}  hl {[len(s['hl']) for s in r['sets']]}  steps {len(r['steps'])}")


if __name__ == "__main__":
    main()
