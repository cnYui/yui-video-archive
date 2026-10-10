# -*- coding: utf-8 -*-
"""译稿_v1.txt + units.json → 录制稿_v1.json，并逐句检查“中文念得完吗”。

  python build_script.py

译稿每行：  范围 | 讲话人 | 英文（清理过口癖、补了标点） | 中文字幕 | 配音文本（可省略 = 同中文字幕）
  范围：U005、U005-U007（含两端，合并几个小句成一句中文），或 t49.55-51.30（直接给原片里的起止秒，用于一个小句里混着两个人说话的地方）。
  讲话人：空 = 她（出镜的演示者）；dot = 她的 AI 助理 dot 的声音。# 开头是注释。
  配音文本里把数字、符号写成念法（“11:30”→“十一点半”），英文产品名保持原样。

检查：窗口 = 这一句原话起点 → 下一句原话起点；预计时长 = 中文字数 ÷ CPS（曼波声线实测约 6.3 字/秒）+ 英文单词数 × 0.38 s；
  预计 > 窗口 × 1.15 + 0.1 的列出来，要改短译文。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CPS = 6.3
EN_WORD = 0.38
MAX_SPEED = 1.18


def est_sec(s):
    s = re.sub(r"[\s，。！？、；：,.!?;:“”‘’\"'（）()…—\-「」]", " ", s)
    cjk = len(re.findall(r"[一-鿿]", s))
    words = len(re.findall(r"[A-Za-z][A-Za-z0-9&]*", s))
    return cjk / CPS + words * EN_WORD, cjk + words


def main():
    units = json.loads((HERE / "units.json").read_text(encoding="utf-8"))
    uid = {u["id"]: u for u in units}
    order = [u["id"] for u in units]
    lines = []
    for raw in (HERE / "译稿_v1.txt").read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue
        parts = [p.strip() for p in raw.split("|")]
        assert len(parts) >= 4, f"列数不够：{raw[:60]}"
        rng, who, en, zh = parts[:4]
        say = parts[4] if len(parts) > 4 and parts[4] else zh
        m = re.fullmatch(r"t(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)", rng)
        if m:
            src = [float(m[1]), float(m[2])]
        else:
            a, _, b = rng.partition("-")
            b = b or a
            assert a in uid and b in uid, f"没有这个编号：{rng}"
            assert order.index(a) <= order.index(b), f"编号顺序反了：{rng}"
            src = [uid[a]["s"], uid[b]["e"]]
        assert who in ("", "dot"), f"讲话人只能是空或 dot：{raw[:40]}"
        lines.append({"range": rng, "who": who, "en": en, "zh": zh, "say": say, "src": src})
    for i, l in enumerate(lines):
        l["id"] = f"N{i + 1:03d}"
    # 顺序和覆盖检查
    for a, b in zip(lines, lines[1:]):
        if b["src"][0] < a["src"][0] - 0.01:
            print(f"!! 顺序不对：{a['id']}（{a['src'][0]}）在 {b['id']}（{b['src'][0]}）前面")
        if b["src"][0] < a["src"][1] - 0.4:
            print(f"!! 原话时间重叠 {a['id']} ({a['src'][0]}–{a['src'][1]}) / {b['id']} ({b['src'][0]}–{b['src'][1]})")
    missing = []
    for u in units:
        dur = max(u["e"] - u["s"], 0.01)
        ov = max((max(0.0, min(u["e"], l["src"][1]) - max(u["s"], l["src"][0])) for l in lines), default=0.0)
        if ov < 0.5 * dur:
            missing.append(u["id"])
    for i, l in enumerate(lines):
        nxt = lines[i + 1]["src"][0] if i + 1 < len(lines) else l["src"][1] + 2.0
        l["window"] = round(max(nxt - l["src"][0], 0.5), 2)
        l["est"], l["n"] = (round(x, 2) for x in est_sec(l["say"]))
    (HERE / "录制稿_v1.json").write_text(json.dumps({"lines": lines}, ensure_ascii=False, indent=1), encoding="utf-8")
    tot = sum(l["est"] for l in lines)
    print(f"{len(lines)} 句，配音文本 {sum(l['n'] for l in lines):.0f} 字（英文单词算 1 个），预计 {tot:.0f} 秒 = {tot / 60:.1f} 分钟；没被引用的小句：{' '.join(missing) or '无'}")
    tight = [l for l in lines if l["est"] > l["window"] * 1.15 + 0.1]
    print(f"偏紧（预计 > 窗口×1.15+0.1）{len(tight)} 句：")
    for l in tight:
        print(f"  {l['id']} {l['range']:>14} 窗口 {l['window']:5.2f}s 预计 {l['est']:5.2f}s  {l['zh'][:46]}")


if __name__ == "__main__":
    main()
