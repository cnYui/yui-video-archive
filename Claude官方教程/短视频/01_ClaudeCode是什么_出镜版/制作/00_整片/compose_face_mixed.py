# -*- coding: utf-8 -*-
r"""出镜小窗（混合版式）：这条视频的场景在单窗 / 双窗 / 大窗之间切换，而技能的 compose_face.py 一条视频只认一个版式（single 或 dual）。
这个包装脚本把技能脚本 import 进来，只替换两件事——每个场景的小窗位置、字幕条检查——其余（三层小画布、镜像、缓动、ffmpeg 合成）全用技能里的原样：

  场景 mode one  → single 版式：小窗居中在字幕下面（x 360, y 1664, 360×360），字幕 y 1498
  场景 mode two / big → dual 版式：小窗缩到 240 放左下角（x 40, y 1460），字幕 y 1764
  plan.json 的场景可写 "face": "center|bl|tl|tr|hide" 覆盖（按该场景所属版式的位置表）。

用法（在本目录）：  python compose_face_mixed.py <本条目录> [--base 整片_v1_cards无小窗.mp4] [--out 整片_v1.mp4] [--seconds N]
face.json：草稿用占位人像（"mirror": false）；悠一的真视频来了换成 src / start / crop，并把 "mirror" 改回 true。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\yui\.claude\skills\short-video\scripts")
import compose_face as cf  # noqa: E402

MODE_LAYOUT = {"one": "single", "two": "dual", "big": "dual"}
HERE = Path(__file__).resolve().parent
_TL = {}


def keyframes(tl, plan, layout, size0, overrides):
    _TL["tl"] = tl
    per = {sc["id"]: sc.get("face") for sc in plan.get("plan", [])}
    per.update(overrides)
    out = []
    for sg in tl["segs"]:
        lay = MODE_LAYOUT[tl["clips"][sg["id"]].get("mode", "two")]
        name = per.get(sg["id"]) or cf.DEFAULT_POS[lay]
        if name == "hide":
            x, y, sz = cf.POS[lay].get("center", (360, 1664, size0))[0], cf.HIDE_Y, size0
        else:
            x, y, sz = cf.POS[lay][name]
            if name == "center" and lay == "single":
                sz = size0
        out.append((sg["s"], x, y, sz / cf.BASE_SIZE))
    return out


def check_subtitle_overlap(kfs, wins, layout, total):
    """字幕条的位置跟着场景走（单窗 y 1490–1620、双窗 / 大窗 y 1756–1884）：逐 0.05 s 采样小窗（含阴影 / 描边 / 贴纸）有没有压到当时的字幕条。"""
    tl = _TL["tl"]
    segs = tl["segs"]
    band = lambda t: cf.SUB_BAND[MODE_LAYOUT[tl["clips"][next(g for g in reversed(segs) if g["s"] <= t + 1e-6)["id"]]["mode"]]]
    hit, t = [], 0.0
    while t <= total:
        x, y, sz = cf.at(kfs, t, wins)
        top, bot = band(t)
        if y - 14 < bot and y + sz + 14 > top:
            hit.append(round(t, 2))
        t += 0.05
    if not hit:
        print("字幕检查：小窗全程没有盖到当时的字幕条")
        return
    runs, start, prev = [], hit[0], hit[0]
    for h in hit[1:]:
        if h - prev > 0.06:
            runs.append((start, prev)); start = h
        prev = h
    runs.append((start, prev))
    for a, b in runs:
        kind = "移动途中扫过" if b - a <= 0.6 else "停着盖住了"
        print(f"⚠ 字幕检查：{a:.2f}–{b:.2f} s 小窗{kind}字幕条")


cf.keyframes = keyframes
cf.check_subtitle_overlap = check_subtitle_overlap

if __name__ == "__main__":
    sys.exit(cf.main())
