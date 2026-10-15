# -*- coding: utf-8 -*-
"""台本.json → 台本.md（给人看的版本：每页的时间码、音乐段落、logo、文案）。JSON 是唯一来源，别直接改 md。"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "台本" / "台本.json"
OUT = HERE.parent / "台本" / "台本.md"

# 音乐段落（拍序号，见 docs/ai/context/20261001-171531-harness-camps-video_CN.md）
# 音乐段落（拍序号 k，一小节 = 4 拍；见记录 20261001-171531-harness-camps-video_CN.md）。查表：取 ≤ k 的最大键
SECTIONS = {0: "前奏（轻）", 20: "前奏后半：上升音扫", 32: "★鼓点进入 1", 33: "主歌", 60: "主歌（k60–63 过门）", 64: "过渡段：低音下滑",
            80: "上升音扫（k92–96 整小节静音）", 96: "★鼓点进入 2", 97: "主歌", 128: "主歌（加层）", 144: "主歌（收尾页）",
            156: "过门 → 自然收尾淡出"}


def section(k):
    return SECTIONS[max(x for x in SECTIONS if x <= k)]


def tc(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def main():
    d = json.loads(SRC.read_text(encoding="utf-8"))
    beat, t0 = 60 / d["bpm"], d["t0"]
    tb = lambda k: t0 + k * beat
    L = d["logos"]
    SB, IB = d.get("slide_beats", 16), d.get("intro_beats", 16)
    out = [f"# {d['title']}（台本，由 build_script_md.py 从 台本.json 生成）", "",
           f"{d['bpm']} BPM，第 0 拍 {t0} s，每页 {SB} 拍（{SB // 4} 小节 = {SB * beat:.2f} s）。画面 2340×1080、30 fps；音轨 = 参考视频的 BGM（只有 BGM，没有人声），在第 160 拍自然收尾处裁掉并淡出，全片 {d['dur']:.1f} s。", "",
           "## 时间线", "", "| 页 | 拍 | 时间 | 音乐 | 内容 |", "|---|---|---|---|---|",
           f"| 标题 | 0–{IB - 1} | {tc(tb(0))} | {section(0)} | {d['intro']['line1']} {d['intro']['line2']} {d['intro']['line3']}；16 个 logo 逐个弹出，开头动画 {d['intro'].get('speed', 1)} 倍速（每 {1 / d['intro'].get('speed', 1):g} 拍一个），在第 {IB} 拍翻页 |"]
    for i, c in enumerate(d["camps"]):
        k = IB + SB * i
        out.append(f"| {i + 1:02d} {c['name']} | {k}–{k + SB - 1} | {tc(tb(k))} | {section(k)} | {' / '.join(L[x]['label'] for x in c['logos'])} |")
    n = len(d["camps"])
    ko = IB + SB * n
    out.append(f"| 收尾 | {ko}–160 | {tc(tb(ko))} | {section(ko)} | {d['outro']['title']} {d['outro']['sub']} |")
    out += ["", "## 文案", ""]
    for i, c in enumerate(d["camps"]):
        out.append(f"### {i + 1:02d} {c['name']}")
        out.append(f"logo：{' / '.join(L[x]['label'] for x in c['logos'])}")
        if c.get("tag"):
            out.append(f"出处（画面上标题下面的小字）：{c['tag']}")
        out.append("")
        out += [f"> {ln}" for ln in c["lines"]]
        if c.get("chip"):
            out.append(f"> `{c['chip']}`")
        out.append(f"> “{c['epithet']}”")
        if c.get("why"):
            out += ["", f"解释（不上画面，可放简介）：{c['why']}"]
        if c.get("note"):
            out += ["", f"（核实：{c['note']}）"]
        out.append("")
    out += ["## 收尾页", "", f"{d['outro']['title']}", f"{d['outro']['sub']}", f"{d['outro']['small']}", ""]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print("written", OUT)


if __name__ == "__main__":
    main()
