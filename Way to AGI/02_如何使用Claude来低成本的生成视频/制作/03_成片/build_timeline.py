# -*- coding: utf-8 -*-
"""成片时间轴：按用户实际录的口播（02_出镜/edit/edit.json）排画面，时间 = 口播里的时间，口播后面接片尾动画。

输出：timeline.json、timeline.js（页面用）。
- 每个画面从它的第一句话前 0.35 秒开始，到下一个画面开始为止；
- 每句字幕带一张“字 → 时刻”对照表（map），来自剪好的口播再做一遍逐词识别（02_出镜/edit/_qa_asr.json），
  页面里的 at("某个词") 按它查这个词在第几秒说出来；识别对不上的句子就按字数在句子里均分。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
EDIT = HERE.parent / "02_出镜" / "edit"
FPS = 30
LEAD = 0.35            # 画面比这一段的第一句话早出现多少秒
CREDITS = 4.8          # 片尾动画（AI科普/片头片尾/outro，DURATION = 4.8 s）

CHAPTERS = {
    "开场": {"title": "开场：Opus 5.5", "items": ["Opus 5.5", "GPT-6 建模", "视觉能力", "它能做视频吗", "一个像素一个像素"]},
    "作品": {"title": "作品展示", "items": []},
    "原理": {"title": "原理：视频是怎么来的", "items": ["扩散模型", "大语言模型", "一秒 30 张图", "HTML + ffmpeg", "为什么用代码"]},
    "拆解": {"title": "拆解：我做的一期视频", "items": ["一期里有什么", "台本", "配音和嘴型", "角色动作", "BGM 和音效", "检查"]},
    "成本": {"title": "成本：跟视频模型比", "items": ["价格", "我的用量", "素材复用", "不是抽卡", "几乎零成本"]},
    "结尾": {"title": "结尾", "items": []},
}
# (画面, 版式, 章节, 目录第几项, 第一句字幕的序号)   版式：A = 出镜大框，B = 出镜缩到左上角 + 目录，C = 作品展示
SCENES = [
    ("intro", "A", "开场", None, 0),
    ("opus55", "B", "开场", 0, 3),
    ("gpt6", "B", "开场", 1, 7),
    ("vision", "B", "开场", 2, 12),
    ("noimage", "B", "开场", 3, 14),
    ("pixels", "B", "开场", 4, 17),
    ("showcase", "C", "作品", None, 26),
    ("question", "A", "原理", None, 37),
    ("diffusion", "B", "原理", 0, 40),
    ("llm", "B", "原理", 1, 43),
    ("frames", "B", "原理", 2, 50),
    ("html", "B", "原理", 3, 53),
    ("capture", "B", "原理", 3, 56),
    ("structure", "B", "原理", 4, 61),
    ("overview", "B", "拆解", 0, 68),
    ("script", "B", "拆解", 1, 72),
    ("voice", "B", "拆解", 2, 77),
    ("actions", "B", "拆解", 3, 80),
    ("bgm", "B", "拆解", 4, 85),
    ("checks", "B", "拆解", 5, 90),
    ("pricetable", "B", "成本", 0, 92),
    ("usage", "B", "成本", 1, 101),
    ("reuse", "B", "成本", 2, 103),
    ("notgacha", "B", "成本", 3, 111),
    ("zerocost", "B", "成本", 4, 118),
    ("outro", "A", "结尾", None, 125),
]


def units(text):
    """估时单位（和页面里的 units() 一样）：汉字 1，英文单词 1.5，数字每位 1.1，逗号类 0.9，句号类 1.6。"""
    u = 0.0
    for m in re.finditer(r"[A-Za-z][A-Za-z\-]*|\d|[一-鿿]|[，、：；,]|[。？！?!]", text):
        s = m.group(0)
        if s[0].isascii() and s[0].isalpha():
            u += 1.5
        elif s.isdigit():
            u += 1.1
        elif s in "，、：；,":
            u += 0.9
        elif s in "。？！?!":
            u += 1.6
        else:
            u += 1.0
    return u


def word_map(cue, words):
    """这句话里“说到第几成”→ 第几秒：用识别出来的词（开始时间 + 累计字数比例）。"""
    ws = [w for w in words if w["e"] > cue["out_s"] - 0.12 and w["s"] < cue["out_e"] + 0.12 and w["w"].strip()]
    pts = [[0.0, cue["out_s"]]]
    if len(ws) >= 2:
        us = [max(units(w["w"]), 0.5) for w in ws]
        tot, acc = sum(us), 0.0
        for w, u in zip(ws, us):
            t = min(max(w["s"], cue["out_s"]), cue["out_e"])
            f = acc / tot
            if f > pts[-1][0] + 1e-6 and t >= pts[-1][1]:
                pts.append([round(f, 4), round(t, 3)])
            acc += u
    pts.append([1.0, cue["out_e"]])
    return pts


def main():
    ed = json.loads((EDIT / "edit.json").read_text(encoding="utf-8"))
    qa = EDIT / "_qa_asr.json"
    words = []
    if qa.exists():
        for seg in json.loads(qa.read_text(encoding="utf-8")):
            words += seg["words"]
    cues = []
    for i, c in enumerate(ed["cues"]):
        cues.append({"i": i, "pid": c["pid"], "zh": c["zh"], "en": c["en"], "s": c["out_s"], "e": c["out_e"],
                     "map": word_map(c, words) if words else [[0, c["out_s"]], [1, c["out_e"]]]})
    narr = ed["total"]
    total = round(round((narr + CREDITS) * FPS) / FPS, 4)
    scenes = []
    for k, (typ, lay, chap, toc, c0) in enumerate(SCENES):
        first = cues[c0]
        if k == 0:
            start = 0.0
        else:
            prev_end = cues[c0 - 1]["e"]
            start = max(prev_end + 0.02, first["s"] - LEAD)
        start = round(round(start * FPS) / FPS, 4)
        c1 = (SCENES[k + 1][4] - 1) if k + 1 < len(SCENES) else len(cues) - 1
        scenes.append({"id": f"S{k + 1:02d}", "type": typ, "layout": lay, "chapter": chap, "toc": toc, "start": start, "cue0": c0, "cue1": c1})
    for k, s in enumerate(scenes):
        s["end"] = scenes[k + 1]["start"] if k + 1 < len(scenes) else round(round(narr * FPS) / FPS, 4)
    scenes.append({"id": f"S{len(scenes) + 1:02d}", "type": "credits", "layout": "F", "chapter": "结尾", "toc": None,
                   "start": scenes[-1]["end"], "end": total, "cue0": len(cues), "cue1": len(cues) - 1})
    tl = {"fps": FPS, "total": total, "narr": narr, "credits": CREDITS, "chapters": CHAPTERS, "scenes": scenes,
          "cues": cues, "holds": ed.get("holds", [])}
    # 作品展示：口播说到第几个例子就换哪个片段（第一页银魂、火影带提示词，第二页 JoJo、第 4 期）；
    # 每个例子念完后口播里留了停顿（edit.json 的 holds），这时片段原声抬起来
    sc = next(s for s in scenes if s["type"] == "showcase")
    p2 = round(cues[29]["s"] - 0.15, 3)
    items = [
        {"key": "gintama", "page": 0, "t0": round(sc["start"] + 0.15, 3), "t1": round(cues[28]["s"] - 0.05, 3)},
        {"key": "naruto", "page": 0, "t0": round(cues[28]["s"] - 0.05, 3), "t1": p2},
        {"key": "jojo", "page": 1, "t0": round(p2 + 0.1, 3), "t1": round(cues[31]["s"] - 0.05, 3)},
        {"key": "ep04", "page": 1, "t0": round(cues[31]["s"] - 0.05, 3), "t1": sc["end"]},
    ]
    for it in items:
        it["n"] = int((it["t1"] - it["t0"] + 0.5) * FPS) + 1          # 抽多少帧
    tl["show"] = {"pages": [sc["start"], p2, sc["end"]], "items": items}
    (HERE / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (HERE / "timeline.js").write_text("window.TL = " + json.dumps(tl, ensure_ascii=False) + ";\n", encoding="utf-8")

    def mmss(x):
        return f"{int(x // 60):02d}:{x % 60:04.1f}"
    print(f"total {mmss(total)} ({total:.2f}s = 口播 {narr:.2f} + 片尾 {CREDITS}), scenes {len(scenes)}, cues {len(cues)}, asr words {len(words)}")
    for s in scenes:
        print(f"  {s['id']} {s['type']:<11} {s['layout']} {mmss(s['start'])}-{mmss(s['end'])} ({s['end'] - s['start']:5.1f}s)  cues {s['cue0']}-{s['cue1']}")


if __name__ == "__main__":
    main()
